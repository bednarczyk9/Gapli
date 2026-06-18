import requests
import os
import base64
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_API_KEY = "gapli_ba90f561bf78bf55652e21b5ed33400b7551219e"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SHOPS = {
    "alejaokazji": 116,
    "hit_bazar": 64,
    "radosnydzieciak": 61,
    "skarbiec_ofert": 63
}

def get_allegro_token(client_id, client_secret):
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    url = "https://allegro.pl/auth/oauth/token?grant_type=client_credentials"
    headers = {"Authorization": f"Basic {auth_header}"}
    resp = requests.post(url, headers=headers)
    return resp.json().get("access_token") if resp.status_code == 200 else None

def get_mandatory_params(cat_id, token):
    if not cat_id: return []
    url = f"https://api.allegro.pl/sale/categories/{cat_id}/parameters"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.allegro.public.v1+json"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200: return []
    required = []
    for p in resp.json().get("parameters", []):
        if p.get("required"):
            ambiguous_id = p.get("options", {}).get("ambiguousValueId")
            valid_options = []
            for d in p.get("dictionary", []):
                if d.get("id") != ambiguous_id:
                    valid_options.append(d["value"])
            required.append({
                "id": p["id"], "name": p["name"], "type": p.get("type"),
                "dictionary": valid_options if valid_options else None
            })
    return required

def rewrite_with_gemini(name, source_desc, mandatory_params, existing_params):
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not set.")
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"
    param_context = ""
    if mandatory_params:
        param_context = "WAŻNE OSTRZEŻENIE: Allegro BEZWZGLĘDNIE WYMAGA poniższych parametrów. Zwróć je w kluczu 'parameters'. ZABRONIONE JEST używanie słów typu 'inny', 'brak', 'nie dotyczy'!\n"
        for m in mandatory_params:
            if m['dictionary']:
                fallback_str = m['dictionary'][0] # Pick the first definitive option as fallback
                param_context += f"- {m['name']} (Wybierz z listy: {', '.join(m['dictionary'][:10])}. Awaryjnie wybierz pierwszą opcję: '{fallback_str}')\n"
            else:
                param_context += f"- {m['name']} (Typ: {m['type']}. Awaryjnie wpisz: '1' dla liczb, lub dowolny konkretny tekst np. 'Standard')\n"

    prompt = f"""Przygotuj JSON dla Allegro.
Nazwa: {name}
Opis źródłowy: {source_desc}
Obecne parametry: {json.dumps(existing_params, ensure_ascii=False) if existing_params else "Brak"}

1. Zachowaj dobre obecne parametry.
2. {param_context}
3. EAN: Upewnij się, że pole "EAN (GTIN)" zawiera tylko i wyłącznie 13 cyfr, usuń spacje i litery.
4. Liczby zapisuj bez zer (np "3", a nie "3.00").

STRUKTURA JSON:
{{
  "name": "max 50 znaków",
  "description": "HTML (p, b, ul, li)",
  "short_description": "max 250 znaków bez HTML",
  "tags": ["tag1", "tag2"],
  "meta_title": "SEO",
  "meta_description": "SEO",
  "parameters": {{ "Nazwa": "Wartość" }}
}}
Zwróć TYLKO JSON."""
    
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"response_mime_type": "application/json"}}
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        return json.loads(resp.json()['candidates'][0]['content']['parts'][0]['text'])
    return None

def fetch_products_missing_descriptions(account_id):
    url = "https://gapli.com/api/products-manager/allegro/products"
    missing_desc = []
    
    # We fetch active products to find those that are listed but miss a description
    # You can also scan other statuses like "pending" if needed
    for status in ["ACTIVE", "PENDING"]:
        page = 1
        while page <= 10:  # Safety limit to avoid infinite loop
            params = {"konto_allegro_id": account_id, "status": status, "limit": 100, "page": page, "mode": "full"}
            resp = requests.get(url, headers=GAPLI_HEADERS, params=params)
            
            if resp.status_code != 200:
                break
                
            data = resp.json()
            products = data.get("products", [])
            if not products:
                break
                
            for p in products:
                # 1. Zero stock filter
                stock = p.get("gapli_product_stock_quantity", 0)
                if stock is None or int(stock) <= 0:
                    continue
                    
                # 2. Check if description is missing
                offer_desc = p.get("allegro_offer_description")
                catalog_desc = p.get("allegro_catalog_description")
                
                if not offer_desc and not catalog_desc:
                    missing_desc.append(p)
                    
            if page >= data.get("totalPages", 1):
                break
            page += 1
            
    logger.info(f"Found {len(missing_desc)} products with > 0 stock missing Allegro descriptions.")
    return missing_desc

def clean_html_for_allegro(html):
    if not html: return ""
    # 1. Extract table data to text if present
    if "<table" in html:
        cells = re.findall(r'<td>(.*?)</td>', html, re.DOTALL)
        table_text = "Parametry: " + ", ".join([re.sub(r'<.*?>', '', c).strip() for c in cells])
        html = re.sub(r'<table.*?</table>', f" {table_text} ", html, flags=re.DOTALL)

    # 2. Normalize tags
    html = html.replace("<strong>", "<b>").replace("</strong>", "</b>")
    html = html.replace("<br>", "\n").replace("<br />", "\n").replace("<br/>", "\n")
    
    # 3. Strip ALL tags except <b>, <ul>, <li>
    html = re.sub(r'</?(?!b|ul|li|/b|/ul|/li)[a-z0-9]+(?:\s+[^>]*)?>', ' ', html, flags=re.IGNORECASE)
    
    # 4. Split by newlines and wrap non-empty chunks in <p>
    lines = [l.strip() for l in html.split("\n") if l.strip()]
    paragraphs = []
    for line in lines:
        # Balance <b> tags
        open_b = len(re.findall(r'<b>', line, re.IGNORECASE))
        close_b = len(re.findall(r'</b>', line, re.IGNORECASE))
        if open_b > close_b: line += "</b>" * (open_b - close_b)
        elif close_b > open_b: line = re.sub(r'^(\s*</b>)+', '', line, flags=re.IGNORECASE)
        paragraphs.append(f"<p>{line}</p>")
    return "".join(paragraphs)

def update_customization(sku, ai_data):
    cleaned_params = {}
    for k, v in ai_data.get("parameters", {}).items():
        val = str(v[0]) if isinstance(v, list) and v else str(v)
        cleaned_params[str(k)] = val
        
    tags = ai_data.get("tags", [])
    if isinstance(tags, str): tags = [t.strip() for t in tags.split(",")]
    
    # SANITIZE HTML
    clean_desc = clean_html_for_allegro(ai_data.get("description"))
        
    payload = {
        "sku": sku, "scope": "user", "platform": "allegro",
        "custom_name": ai_data.get("name")[:50] if ai_data.get("name") else None,
        "custom_description": clean_desc,
        "custom_short_description": ai_data.get("short_description")[:250] if ai_data.get("short_description") else None,
        "custom_tags": tags[:10],
        "custom_meta_title": ai_data.get("meta_title")[:60] if ai_data.get("meta_title") else None,
        "custom_meta_description": ai_data.get("meta_description")[:160] if ai_data.get("meta_description") else None,
        "custom_parameters": cleaned_params,
        "is_active": True, "images_mode": "replace"
    }
    resp = requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=payload)
    return resp.status_code in [200, 201]

def permanent_delete(product_id, account_id):
    del_url = "https://gapli.com/api/products-manager/allegro/permanent-delete"
    payload = {
        "mode": "selected",
        "product_ids": [{"id": str(product_id), "konto_allegro_id": str(account_id)}]
    }
    resp = requests.delete(del_url, headers=GAPLI_HEADERS, json=payload)
    return resp.status_code == 200

def repair_missing_description(p, allegro_token):
    sku = p.get("sku")
    p_id = p.get("id")
    account_id = p.get("konto_allegro_id")
    cat_id = p.get("allegro_catalog_category_id")
    
    logger.info(f"--- Processing SKU: {sku} (Acc: {account_id}) ---")
    
    # 1. AI Generation
    name = p.get("gapli_product_name") or "Produkt"
    desc = p.get("gapli_product_description") or ""
    
    existing_params = {}
    forbidden_values = ["inny", "brak", "nie dotyczy", "pozostałe", "nieokreślony"]
    raw_params = p.get("allegro_catalog_parameters") or []
    for item in raw_params:
        k = item.get("name")
        v = item.get("valuesLabels")[0] if item.get("valuesLabels") else (item.get("values")[0] if item.get("values") else None)
        if k and v:
            if str(v).lower() not in forbidden_values:
                existing_params[str(k)] = str(v)
            
    mandatory = get_mandatory_params(cat_id, allegro_token)
    ai_data = rewrite_with_gemini(name, desc, mandatory, existing_params)
    
    if not ai_data:
        logger.error("AI Generation failed. Skipping.")
        return False
        
    # 2. Save Customization
    if not update_customization(sku, ai_data):
        logger.error("Failed to save customization. Skipping.")
        return False
    logger.info("Customization saved.")
    
    # 3. Permanent Delete if stuck or has history of errors
    # This clears cached errors like 'ambiguous color' or 'missing ending tag'
    if permanent_delete(p_id, account_id):
        logger.info("Cleared stuck record via permanent-delete.")
        time.sleep(2)
    
    # 4. Re-send
    if not send_to_allegro(sku, account_id):
        logger.error("Failed to sync product to Allegro.")
        return False
    logger.info("Product sync triggered successfully!")
    
    return True

def run_pipeline(shop_name):
    account_id = SHOPS.get(shop_name)
    if not account_id: return
    
    client_id = os.environ.get(f"{shop_name}_client_id") or os.environ.get("skarbiec_client_id")
    client_secret = os.environ.get(f"{shop_name}_client_secret") or os.environ.get("skarbiec_client_secret")
    
    allegro_token = get_allegro_token(client_id, client_secret)
    if not allegro_token:
        logger.error("Missing Allegro token.")
        return
        
    products = fetch_products_missing_descriptions(account_id)
    logger.info(f"Total actionable products found for {shop_name}: {len(products)}")
    
    for p in products:
        repair_missing_description(p, allegro_token)
        time.sleep(3) # Throttle

if __name__ == "__main__":
    # Example execution: python pipeline/repair_missing_descriptions.py hit_bazar
    import sys
    shop = sys.argv[1] if len(sys.argv) > 1 else "skarbiec_ofert"
    run_pipeline(shop)

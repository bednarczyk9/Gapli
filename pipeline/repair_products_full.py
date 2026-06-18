import requests
import os
import base64
import json
import logging
import time
import sys
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SHOPS = {
    "alejaokazji": 116,
    "hit_bazar": 64,
    "radosnydzieciak": 61,
    "skarbiec_ofert": 63
}

def get_allegro_token(client_id, client_secret):
    if not client_id or not client_secret: return None
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    url = "https://allegro.pl/auth/oauth/token?grant_type=client_credentials"
    headers = {"Authorization": f"Basic {auth_header}"}
    try:
        resp = requests.post(url, headers=headers)
        return resp.json().get("access_token") if resp.status_code == 200 else None
    except Exception as e:
        logger.error(f"Error getting Allegro token: {e}")
        return None

def get_mandatory_params(cat_id, token):
    if not cat_id: return []
    url = f"https://api.allegro.pl/sale/categories/{cat_id}/parameters"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.allegro.public.v1+json"}
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200: return []
        required = []
        for p in resp.json().get("parameters", []):
            if p.get("required"):
                required.append({
                    "id": p["id"],
                    "name": p["name"],
                    "type": p.get("type"),
                    "dictionary": [d["value"] for d in p.get("dictionary", [])] if p.get("dictionary") else None
                })
        return required
    except Exception as e:
        logger.error(f"Error getting parameters: {e}")
        return []

def rewrite_with_gemini(name, source_desc, mandatory_params, existing_params):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    param_context = ""
    if mandatory_params:
        param_context = "WAŻNE OSTRZEŻENIE: Allegro BEZWZGLĘDNIE WYMAGA poniższych parametrów. MUSISZ umieścić każdy z nich w wynikowym JSON w obiekcie 'parameters'.\n"
        param_context += "Przeszukaj opis i nazwę produktu, aby znaleźć odpowiednią wartość. Jeśli informacji nie ma, MUSISZ użyć wartości awaryjnej podanej poniżej!\n\n"
        for m in mandatory_params:
            if m['dictionary']:
                fallback_opts = [val for val in m['dictionary'] if val.lower() in ['inny', 'inna', 'inne', 'brak', 'nie dotyczy', 'pozostałe', 'inna marka', 'bez marki', 'nie określono']]
                fallback_str = fallback_opts[0] if fallback_opts else m['dictionary'][-1]
                opts = ", ".join(m['dictionary'][:15])
                param_context += f"- {m['name']} (Wybierz jedną z: {opts}. Awaryjnie: '{fallback_str}')\n"
            elif m['type'] in ['integer', 'float']:
                param_context += f"- {m['name']} (Typ: Liczba. Awaryjnie wpisz: '1')\n"
            else:
                param_context += f"- {m['name']} (Typ: Tekst. Awaryjnie wpisz: 'Producent nieznany' lub 'Brak')\n"

    prompt = f"""
    Jesteś ekspertem Allegro. Przygotuj PEŁNY PAKIET danych produktu w formacie JSON.
    
    DANE WEJŚCIOWE:
    Nazwa: {name}
    Opis źródłowy: {source_desc}
    Obecne parametry produktu (ZACHOWAJ JE!): {json.dumps(existing_params, ensure_ascii=False) if existing_params else "Brak"}
    
    ZADANIE DOTYCZĄCE PARAMETRÓW:
    1. **PIERWSZEŃSTWO MAJĄ** 'Obecne parametry produktu'. Jeśli parametr tam jest i jest sensowny (np. Marka, Model), ZACHOWAJ GO NIEZMIENIONEGO.
    2. {param_context}
    3. Bardzo ważne: Liczby (np. waga) zapisuj bez zbędnych zer na końcu (np. "3" zamiast "3.000").
    
    STRUKTURA JSON:
    {{
      "name": "Poprawiona nazwa produktu (max 50 znaków!)",
      "description": "Poprawiony kod HTML (Tylko p, b, ul, li)",
      "short_description": "Krótki opis bez HTML (max 250 znaków)",
      "tags": ["tag1", "tag2"],
      "meta_title": "SEO Title (max 60 znaków)",
      "meta_description": "SEO Description (max 160 znaków)",
      "parameters": {{ "Nazwa": "Wartość" }}
    }}
    
    Zwróć TYLKO czysty JSON.
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"response_mime_type": "application/json"}}
    
    try:
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            text = resp.json()['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text)
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
    return None

def fetch_products_with_errors(account_id):
    url = f"https://gapli.com/api/products-manager/allegro/products"
    statuses = ["ERROR", "VALIDATION_ERROR"]
    all_failed = []
    for status in statuses:
        params = {"konto_allegro_id": account_id, "status": status, "limit": 20, "page": 1, "mode": "full"}
        resp = requests.get(url, headers=GAPLI_HEADERS, params=params)
        if resp.status_code == 200:
            products = resp.json().get("products", [])
            # Filter out products with zero stock to save API calls
            active_products = [p for p in products if p.get("gapli_product_stock_quantity", 0) > 0]
            if len(active_products) < len(products):
                logger.info(f"Skipped {len(products) - len(active_products)} products with 0 stock in status {status}.")
            all_failed.extend(active_products)
    return all_failed

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

def permanent_delete(product_id, account_id):
    del_url = "https://gapli.com/api/products-manager/allegro/permanent-delete"
    payload = {
        "mode": "selected",
        "product_ids": [{"id": str(product_id), "konto_allegro_id": str(account_id)}]
    }
    resp = requests.delete(del_url, headers=GAPLI_HEADERS, json=payload)
    return resp.status_code == 200

def fix_product(p, allegro_token, account_id):
    sku = p.get("sku")
    p_id = p.get("id")
    name = p.get("gapli_product_name") or p.get("allegro_catalog_product_name") or "Produkt"
    desc = p.get("gapli_product_description") or p.get("allegro_catalog_description") or ""
    cat_id = p.get("allegro_catalog_category_id") or p.get("allegro_offer_category_id")
    
    existing_raw = p.get("gapli_product_parameters") or p.get("allegro_catalog_parameters") or p.get("gapli_product_attributes") or []
    existing_params = {}
    forbidden_values = ["inny", "brak", "nie dotyczy", "pozostałe", "inna marka", "bez marki", "nie określono"]
    
    if isinstance(existing_raw, list):
        for item in existing_raw:
            if isinstance(item, dict):
                k = item.get("name") or item.get("id")
                v = item.get("valuesLabels")[0] if item.get("valuesLabels") else (item.get("values")[0] if item.get("values") else item.get("value"))
                if k and v and str(v).lower() not in forbidden_values:
                    existing_params[str(k)] = str(v)
    elif isinstance(existing_raw, dict):
        existing_params = {str(k): str(v) for k, v in existing_raw.items() if v and str(v).lower() not in forbidden_values}

    logger.info(f"Fixing SKU: {sku} (Category: {cat_id})")
    
    mandatory = get_mandatory_params(cat_id, allegro_token)
    ai_data = rewrite_with_gemini(name, desc, mandatory, existing_params)
    
    if ai_data:
        cleaned_params = {}
        for k, v in ai_data.get("parameters", {}).items():
            val = str(v[0]) if isinstance(v, list) and v else str(v)
            if "." in val:
                try:
                    fval = float(val.replace(",", "."))
                    val = str(int(fval)) if fval == int(fval) else str(fval)
                except: pass
            cleaned_params[str(k)] = val
        
        tags = ai_data.get("tags", [])
        if isinstance(tags, str): tags = [t.strip() for t in tags.split(",") if t.strip()]
        if isinstance(tags, list): tags = [str(t)[:40] for t in tags[:10]]
        
        # SANITIZE HTML
        clean_desc = clean_html_for_allegro(ai_data.get("description"))
            
        payload = {
            "sku": sku, "scope": "user", "platform": "allegro",
            "custom_name": ai_data.get("name")[:50] if ai_data.get("name") else None,
            "custom_description": clean_desc,
            "custom_short_description": ai_data.get("short_description")[:250] if ai_data.get("short_description") else None,
            "custom_tags": tags,
            "custom_meta_title": ai_data.get("meta_title")[:60] if ai_data.get("meta_title") else None,
            "custom_meta_description": ai_data.get("meta_description")[:160] if ai_data.get("meta_description") else None,
            "custom_parameters": cleaned_params,
            "is_active": True, "images_mode": "replace"
        }
        
        save_resp = requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=payload)
        
        if save_resp.status_code in [200, 201]:
            logger.info(f"  SUCCESS: Customization saved for {sku}")
            
            # FORCE FRESH START VIA PERMANENT DELETE
            if permanent_delete(p_id, account_id):
                logger.info(f"  Nuked old record for {sku} to clear errors.")
                time.sleep(2)

            # Trigger sync via marketplace listing endpoint
            api_key = os.environ.get("Gapli_Apikey")
            if api_key:
                send_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
                send_headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                send_body = {"action": "send", "account_id": str(account_id), "product_skus": [sku], "force_update": True}
                requests.post(send_url, headers=send_headers, json=send_body)
                logger.info(f"  Triggered marketplace fresh send for {sku}")
            return True
        else:
            logger.error(f"  FAILED to save customization for {sku}: {save_resp.status_code} {save_resp.text}")
    return False

def main():
    shop_name = sys.argv[1].lower() if len(sys.argv) > 1 else "skarbiec_ofert"
    target_sku = sys.argv[2] if len(sys.argv) > 2 else None
    
    if shop_name not in SHOPS:
        logger.error(f"Invalid shop. Available: {list(SHOPS.keys())}")
        return

    account_id = SHOPS[shop_name]
    client_id = os.environ.get(f"{shop_name}_client_id") or os.environ.get("skarbiec_client_id")
    client_secret = os.environ.get(f"{shop_name}_client_secret") or os.environ.get("skarbiec_client_secret")
    
    if not client_id or not client_secret:
        logger.error("Missing Allegro credentials.")
        return

    allegro_token = get_allegro_token(client_id, client_secret)
    if not allegro_token: return
        
    if target_sku:
        url = f"https://gapli.com/api/products-manager/allegro/products"
        resp = requests.get(url, headers=GAPLI_HEADERS, params={"konto_allegro_id": account_id, "search": target_sku, "mode": "full"})
        failed_products = resp.json().get("products", []) if resp.status_code == 200 else []
    else:
        failed_products = fetch_products_with_errors(account_id)
    
    logger.info(f"Processing {len(failed_products)} products (LIMIT: 1 fix per run).")
    
    count = 0
    for p in failed_products:
        if fix_product(p, allegro_token, account_id):
            count += 1
            break # STRICT USER LIMIT: 1 PRODUCT PER TEST
        time.sleep(2)
            
    logger.info(f"Finished. Total fixed: {count}")

if __name__ == "__main__":
    main()

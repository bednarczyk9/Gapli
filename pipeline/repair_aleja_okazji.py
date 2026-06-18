import requests
import json
import logging
import time
import os
import base64

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json", "Accept": "application/json"}
ACCOUNT_ID = "116" # AlejaOkazji

ALLEGRO_CLIENT_ID = os.environ.get("skarbiec_client_id")
ALLEGRO_CLIENT_SECRET = os.environ.get("skarbiec_client_secret")

def get_allegro_token():
    if not ALLEGRO_CLIENT_ID or not ALLEGRO_CLIENT_SECRET:
        return None
    auth_header = base64.b64encode(f"{ALLEGRO_CLIENT_ID}:{ALLEGRO_CLIENT_SECRET}".encode()).decode()
    url = "https://allegro.pl/auth/oauth/token?grant_type=client_credentials"
    headers = {"Authorization": f"Basic {auth_header}"}
    try:
        resp = requests.post(url, headers=headers, timeout=10)
        return resp.json().get("access_token") if resp.status_code == 200 else None
    except: return None

def get_mandatory_params(cat_id, token):
    if not cat_id or not token: return []
    url = f"https://api.allegro.pl/sale/categories/{cat_id}/parameters"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.allegro.public.v1+json"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200: return []
        required = []
        for p in resp.json().get("parameters", []):
            if p.get("required"):
                required.append({
                    "name": p["name"],
                    "dictionary": [d["value"] for d in p.get("dictionary", [])]
                })
        return required
    except: return []

def repair_product(p, allegro_token):
    sku = p.get('sku')
    cat_id = p.get("allegro_catalog_category_id") or p.get("allegro_offer_category_id")
    name = p.get("gapli_product_name") or p.get("allegro_catalog_product_name")
    source = (p.get("gapli_product_description") or p.get("allegro_offer_description") or "")
    
    logger.info(f"Repairing SKU: {sku}...")
    
    mandatory = get_mandatory_params(cat_id, allegro_token)
    param_context = ""
    if mandatory:
        param_context = "\n".join([f"- {m['name']} (Dozwolone wartości: {', '.join(m['dictionary'][:10])})" for m in mandatory])
    
    prompt = (
        "Przygotuj PEŁNY PAKIET danych produktu (tytuł, opis HTML, krótki opis, tagi, parametry, SEO).\n"
        "ZWRÓĆ WYNIK W FORMIE JSON.\n"
        "WAŻNE: Wyodrębnij parametry techniczne. "
    )
    if param_context:
        prompt += f"Allegro WYMAGA poniższych parametrów. Musisz wybrać dla nich najbardziej pasujące wartości ze słownika:\n{param_context}\n"
    
    prompt += f"STRUKTURA HTML: h1, h2, p, ul, ol, li, b, br. ZAKAZ <i>.\nDane źródłowe: {source[:3000]}"
    
    ai_payload = {
        "provider_id": 1, "sku": sku, "platform": "allegro", "generation_type": "all", 
        "model": "gemini-3.5-flash", "product_data": {"name": name, "parameters": []},
        "custom_prompt": prompt
    }
    
    ai_resp = requests.post("https://gapli.com/api/product-customizer/ai/generate", headers=GAPLI_HEADERS, json=ai_payload)
    if ai_resp.status_code != 200:
        logger.error(f"  AI Generation failed: {ai_resp.status_code}")
        return False
        
    try:
        clean_text = ai_resp.json().get("result", {}).get("description", "").strip()
        if "```" in clean_text: clean_text = clean_text.split("```")[1].split("```")[0].strip()
        if clean_text.startswith("json"): clean_text = clean_text[4:].strip()
        ai_data = json.loads(clean_text)
        
        save_payload = {
            "sku": sku, "scope": "user", "platform": "allegro",
            "custom_name": ai_data.get("name"),
            "custom_description": ai_data.get("description"),
            "custom_parameters": ai_data.get("parameters"),
            "is_active": True, "images_mode": "replace"
        }
        save_resp = requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=save_payload)
        if save_resp.status_code in [200, 201]:
            logger.info(f"  SUCCESS: SKU {sku} repaired and customization saved.")
            return True
        else:
            logger.error(f"  Failed to save customization: {save_resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"  Error parsing/saving for {sku}: {e}")
        return False

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
GAPLI_INTEGRATIONS_HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}

def resend_to_marketplace(skus):
    logger.info(f"Resending {len(skus)} products to marketplace...")
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    body = {
        "action": "send",
        "account_id": ACCOUNT_ID,
        "product_skus": skus,
        "price_range": {"min": 50, "max": 50000}
    }
    resp = requests.post(url, headers=GAPLI_INTEGRATIONS_HEADERS, json=body)
    if resp.status_code == 200:
        logger.info(f"  Marketplace send response: {resp.json().get('message')}")
    else:
        logger.error(f"  Failed to resend: {resp.status_code} {resp.text}")

def main():
    allegro_token = get_allegro_token()
    if not allegro_token:
        logger.warning("No Allegro token (skarbiec_client_id/secret missing). Repair will be less precise.")

    # 1. Fetch products with errors
    logger.info(f"Fetching products with errors for account {ACCOUNT_ID}...")
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&limit=100&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200:
        logger.error(f"Failed to fetch products: {resp.status_code}")
        return

    products = resp.json().get("products", [])
    repaired_skus = []
    need_resend = []

    for p in products:
        sku = p.get('sku')
        api_resp = p.get('allegro_api_response') or {}
        api_errors = api_resp.get('errors') or []
        
        has_validation_error = False
        has_limit_error = False
        
        for err in api_errors:
            code = err.get('code', '')
            if "Validation" in code or "Parameters" in code or "Title" in code:
                has_validation_error = True
            if "MaxInactiveOffers" in code:
                has_limit_error = True

        if has_validation_error:
            if repair_product(p, allegro_token):
                repaired_skus.append(sku)
                need_resend.append(sku)
                time.sleep(2)
        elif has_limit_error:
            # We can't repair limit error via AI, but maybe just resending works if some drafts were cleared?
            # For now, let's just collect them for resend attempt.
            need_resend.append(sku)
        elif p.get('allegro_sync_upload_error_message') == "🛡️ PEI BLOCKED: unresolved marketplace error":
             # Try resending these too
             need_resend.append(sku)

    if need_resend:
        # Resend in batches of 20
        for i in range(0, len(need_resend), 20):
            batch = need_resend[i:i+20]
            resend_to_marketplace(batch)
            time.sleep(5)

    logger.info(f"Task completed. Repaired: {len(repaired_skus)}, Resent attempts: {len(need_resend)}")

if __name__ == "__main__":
    main()

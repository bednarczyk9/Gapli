import requests
import os
import base64
import json
import logging
import time
import re
from datetime import datetime

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json", "Accept": "application/json"}
ACCOUNTS = ["61", "64", "116", "308", "146", "145", "142", "144"]

ALLEGRO_CLIENT_ID = os.environ.get("skarbiec_client_id")
ALLEGRO_CLIENT_SECRET = os.environ.get("skarbiec_client_secret")

def get_allegro_token():
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

def fix_sku_proactively(sku, acc_id, allegro_token):
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc_id}&search={sku}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200 or not resp.json().get("products"): return False
    p = resp.json()["products"][0]
    
    cat_id = p.get("allegro_catalog_category_id") or p.get("allegro_offer_category_id")
    name = p.get("gapli_product_name") or p.get("allegro_catalog_product_name")
    source = p.get("gapli_product_description") or p.get("allegro_offer_description")
    
    mandatory = get_mandatory_params(cat_id, allegro_token)
    param_context = "\n".join([f"- {m['name']} (Dozwolone wartości: {', '.join(m['dictionary'][:10])})" for m in mandatory])
    
    prompt = (
        "Przygotuj PEŁNY PAKIET danych produktu (tytuł, opis HTML, krótki opis, tagi, parametry, SEO).\n"
        "ZWRÓĆ WYNIK W FORMIE JSON.\n"
        "WAŻNE: Allegro WYMAGA poniższych parametrów. Musisz wybrać dla nich najbardziej pasujące wartości ze słownika:\n"
        f"{param_context}\n"
        "STRUKTURA HTML: TYLKO h1, h2, p, ul, ol, li, b, br. ZAKAZ <i>, div, span, style.\n"
        f"Dane źródłowe: {source[:3000]}"
    )
    
    ai_payload = {
        "provider_id": 1, "sku": sku, "platform": "allegro", "generation_type": "all", 
        "model": "gemini-3.5-flash", "product_data": {"name": name, "parameters": []},
        "custom_prompt": prompt
    }
    
    ai_resp = requests.post("https://gapli.com/api/product-customizer/ai/generate", headers=GAPLI_HEADERS, json=ai_payload)
    if ai_resp.status_code != 200: return False
    ai_text = ai_resp.json().get("result", {}).get("description", "")
    
    try:
        clean_text = ai_text.strip()
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
        return save_resp.status_code in [200, 201]
    except: return False

def scan_and_repair_v2():
    total_repaired = 0
    allegro_token = get_allegro_token()
    
    for acc_id in ACCOUNTS:
        logger.info(f"Scanning Account {acc_id} for sync errors...")
        page = 1
        while True:
            url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc_id}&allegro_sync_upload_status=error&limit=100&page={page}&mode=full"
            resp = requests.get(url, headers=GAPLI_HEADERS)
            if resp.status_code != 200: break
            
            data = resp.json()
            products = data.get("products", [])
            if not products: break
            
            for p in products:
                sku = p.get("sku")
                error_msg = str(p.get("allegro_sync_upload_error_message") or "").lower()
                
                # Check for fixable error patterns
                is_fixable = (
                    "missing ending tag" in error_msg or 
                    "invalid html subset" in error_msg or
                    "productvalidationexception" in error_msg or
                    "parametrów wymaganych" in error_msg
                )
                
                if is_fixable:
                    logger.info(f"Repairing {sku}...")
                    if fix_sku_proactively(sku, acc_id, allegro_token):
                        logger.info(f"  -> SUCCESS: SKU {sku} repaired.")
                        total_repaired += 1
                        time.sleep(3) # Safe delay
                        if total_repaired >= 30: return # Stop after 30 to avoid rate limits
                    else:
                        logger.warning(f"  -> FAILED: SKU {sku}")
            
            if page >= data.get("total_pages", 1): break
            page += 1
            if page > 100: break 
            
    logger.info(f"Batch finished. Repaired: {total_repaired}")

if __name__ == "__main__":
    scan_and_repair_v2()

import requests
import json
import logging
import time
import pandas as pd
import os
import base64
from datetime import datetime

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json", "Accept": "application/json"}
ACCOUNT_ID = "61"

ALLEGRO_CLIENT_ID = os.environ.get("skarbiec_client_id")
ALLEGRO_CLIENT_SECRET = os.environ.get("skarbiec_client_secret")

# --- Allegro API Helpers ---

def get_allegro_token():
    if not ALLEGRO_CLIENT_ID or not ALLEGRO_CLIENT_SECRET:
        logger.error("Allegro credentials missing in environment variables.")
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

# --- Gapli Processing Logic ---

def get_data_maps():
    logger.info("Fetching all customizations...")
    customized_skus = set()
    page = 1
    while True:
        url = f"https://gapli.com/api/product-customizer/customizations-list?page={page}&limit=100"
        resp = requests.get(url, headers=GAPLI_HEADERS)
        if resp.status_code != 200: break
        data = resp.json()
        items = data.get("items", [])
        if not items: break
        for item in items:
            sku = item.get("sku")
            if sku: customized_skus.add(sku)
        if page >= data.get("total_pages", 1): break
        page += 1
    
    logger.info(f"Total customized SKUs: {len(customized_skus)}")
    
    logger.info("Fetching active products to build EAN map...")
    customized_eans = set()
    page = 1
    while True:
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&status=ACTIVE&limit=100&page={page}"
        resp = requests.get(url, headers=GAPLI_HEADERS)
        if resp.status_code != 200: break
        data = resp.json()
        products = data.get("products", [])
        if not products: break
        for p in products:
            sku = p.get("sku")
            ean = p.get("gapli_product_global_unique_id") or p.get("ean")
            if sku in customized_skus and ean: customized_eans.add(ean)
        if page >= data.get("total_pages", 1) or page > 50: break
        page += 1
    logger.info(f"Identified {len(customized_eans)} EANs with customizations.")
    return customized_skus, customized_eans

def format_description(desc_obj):
    if not desc_obj: return ""
    if isinstance(desc_obj, str): return desc_obj
    if isinstance(desc_obj, dict) and "sections" in desc_obj:
        text_parts = []
        for section in desc_obj.get("sections", []):
            for item in section.get("items", []):
                if item.get("type") == "TEXT": text_parts.append(item.get("content", ""))
        return "\n".join(text_parts)
    return str(desc_obj)

def process_batch(limit=100):
    customized_skus, customized_eans = get_data_maps()
    allegro_token = get_allegro_token()
    
    logger.info(f"Scanning for candidates for 'Full Package' AI...")
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&status=ACTIVE&limit={limit}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
        
    products = resp.json().get("products", [])
    candidates = []
    for p in products:
        sku = p.get("sku")
        ean = p.get("gapli_product_global_unique_id") or p.get("ean")
        if sku in customized_skus or (ean and ean in customized_eans): continue
            
        offer_desc = p.get("allegro_offer_description")
        catalog_desc = p.get("allegro_catalog_description")
        gapli_desc = p.get("gapli_product_description")
        
        source_description = None
        if offer_desc or catalog_desc: continue
            
        if gapli_desc: source_description = gapli_desc
        elif ean:
            cat_url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&ean={ean}&mode=full"
            cat_resp = requests.get(cat_url, headers=GAPLI_HEADERS)
            if cat_resp.status_code == 200:
                for cat_p in cat_resp.json().get("products", []):
                    desc = cat_p.get("allegro_catalog_description") or cat_p.get("gapli_product_description")
                    if desc: source_description = desc; break
        
        if source_description:
            candidates.append({
                "sku": sku, "ean": ean,
                "cat_id": p.get("allegro_catalog_category_id") or p.get("allegro_offer_category_id"),
                "name": p.get("gapli_product_name") or p.get("allegro_catalog_product_name"),
                "description": format_description(source_description),
                "parameters": p.get("gapli_product_attributes") or p.get("parameters") or []
            })
            
    logger.info(f"Found {len(candidates)} candidates.")
    
    processed_results = []
    for i, cand in enumerate(candidates):
        sku = cand["sku"]
        logger.info(f"[{i+1}/{len(candidates)}] Processing {sku}...")
        
        # Proactive: Get mandatory params from Allegro
        mandatory = get_mandatory_params(cand["cat_id"], allegro_token) if allegro_token else []
        param_context = ""
        if mandatory:
            param_context = "\nBARDZO WAŻNE: Allegro WYMAGA tych parametrów. Wybierz KROTKIE wartości ze słownika:\n" + \
                            "\n".join([f"- {m['name']} (Dozwolone: {', '.join(m['dictionary'][:10])})" for m in mandatory])

        result_entry = {"sku": sku, "ean": cand["ean"], "status": "failed", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        try:
            prompt = (
                "Przygotuj PEŁNY PAKIET danych produktu (tytuł, opis HTML, krótki opis, tagi, parametry, SEO).\n"
                "ZWRÓĆ WYNIK W FORMIE JSON (name, description, short_description, tags, meta_title, meta_description, parameters).\n"
                "ZASADY:\n"
                "1. HTML: TYLKO h1, h2, p, ul, ol, li, b, br. (ZAKAZ <i>, div, span, style).\n"
                "2. PARAMETRY: Każdy musi mieć krótką wartość słownikową."
                f"{param_context}\n"
                f"Dane źródłowe: {cand['description'][:3000]}"
            )
            
            ai_payload = {
                "provider_id": 1, "sku": sku, "platform": "allegro", "generation_type": "all", 
                "model": "gemini-3.5-flash", "product_data": {"name": cand["name"], "parameters": cand["parameters"]},
                "custom_prompt": prompt
            }
            
            ai_resp = requests.post("https://gapli.com/api/product-customizer/ai/generate", headers=GAPLI_HEADERS, json=ai_payload)
            if ai_resp.status_code != 200: continue
                
            ai_text = ai_resp.json().get("result", {}).get("description", "")
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
            if save_resp.status_code in [200, 201]:
                result_entry["status"] = "success"
                if cand["ean"]: customized_eans.add(cand["ean"])
            else: result_entry["error"] = f"Save failed: {save_resp.status_code}"
            time.sleep(1.5)
        except Exception as e: result_entry["error"] = str(e)
        processed_results.append(result_entry)

    if processed_results:
        report_path = f"reports/ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        pd.DataFrame(processed_results).to_excel(report_path, index=False)

if __name__ == "__main__":
    process_batch(limit=100)

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
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

ALLEGRO_CLIENT_ID = os.environ.get("skarbiec_client_id")
ALLEGRO_CLIENT_SECRET = os.environ.get("skarbiec_client_secret")

def get_allegro_token():
    auth_header = base64.b64encode(f"{ALLEGRO_CLIENT_ID}:{ALLEGRO_CLIENT_SECRET}".encode()).decode()
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
            required.append({
                "name": p["name"],
                "dictionary": [d["value"] for d in p.get("dictionary", [])]
            })
    return required

def fix_sku_proactively(sku, acc_id, allegro_token):
    logger.info(f"Proactive fix for SKU: {sku}")
    
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc_id}&search={sku}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200 or not resp.json().get("products"): return False
    p = resp.json()["products"][0]
    
    cat_id = p.get("allegro_catalog_category_id") or p.get("allegro_offer_category_id")
    name = p.get("gapli_product_name") or p.get("allegro_catalog_product_name")
    source = p.get("gapli_product_description") or p.get("allegro_offer_description")
    
    mandatory = get_mandatory_params(cat_id, allegro_token)
    logger.info(f"  Category {cat_id} requires: {[m['name'] for m in mandatory]}")
    
    param_context = "\n".join([f"- {m['name']} (Dozwolone wartości: {', '.join(m['dictionary'][:10])})" for m in mandatory])
    
    prompt = (
        "Przygotuj PEŁNY PAKIET danych produktu (tytuł, opis HTML, krótki opis, tagi, parametry, SEO).\n"
        "ZWRÓĆ WYNIK W FORMIE JSON.\n"
        "WAŻNE: Allegro WYMAGA poniższych parametrów. Musisz wybrać dla nich najbardziej pasujące wartości ze słownika:\n"
        f"{param_context}\n"
        "STRUKTURA HTML: TYLKO h1, h2, p, ul, ol, li, b, br. ZAKAZ <i>.\n"
        f"Dane źródłowe: {source[:3000]}"
    )
    
    ai_payload = {
        "provider_id": 1, "sku": sku, "platform": "allegro", "generation_type": "all", 
        "model": "gemini-3.5-flash", "product_data": {"name": name, "parameters": []},
        "custom_prompt": prompt
    }
    
    ai_resp = requests.post("https://gapli.com/api/product-customizer/ai/generate", headers=GAPLI_HEADERS, json=ai_payload)
    if ai_resp.status_code != 200:
        logger.error(f"AI API Error: {ai_resp.status_code}")
        return False
        
    ai_text = ai_resp.json().get("result", {}).get("description", "")
    if not ai_text:
        logger.error("AI returned empty result")
        return False

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
        if save_resp.status_code in [200, 201]:
            logger.info(f"SUCCESS: SKU {sku} fixed proactively.")
            return True
        else:
            logger.error(f"Save Error: {save_resp.status_code}")
    except Exception as e:
        logger.error(f"Processing Error: {e}")
        logger.error(f"AI Text was: {ai_text[:200]}...")
    return False

if __name__ == "__main__":
    token = get_allegro_token()
    if token:
        fix_sku_proactively("1004260-660_150", "61", token)

import requests
import json
import logging
import time
from datetime import datetime

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json", "Accept": "application/json"}
ACCOUNTS = ["61", "64", "116", "308", "146", "145", "142", "144"]

import re

def fix_with_fresh_ai(sku, current_name, source_desc, missing_params=None):
    """Triggers a fresh AI generation and overwrites the customization."""
    logger.info(f"  -> Triggering fresh AI repair for {sku}...")
    
    param_instruction = ""
    if missing_params:
        param_instruction = f"\nBARDZO WAŻNE: Allegro wymaga uzupełnienia parametrów: {', '.join(missing_params)}. \n" \
                            f"Dla każdego z nich podaj KROTKĄ, STANDARDOWĄ wartość (np. dla 'Rodzaj montażu' użyj 'bezinwazyjny' lub 'naścienny' lub 'przykręcany'). \n" \
                            f"Używaj tylko prostych słów, które pasują do słownika Allegro."

    prompt = (
        "Przygotuj PEŁNY PAKIET danych produktu (tytuł, opis HTML, krótki opis, tagi, parametry, SEO).\n"
        "ZWRÓĆ WYNIK W FORMIE JSON zawierającego klucze:\n"
        "name, description, short_description, tags, meta_title, meta_description, parameters (lista {name, value}).\n"
        "ZASADY DLA PARAMETRÓW:\n"
        "- Każdy parametr musi mieć krótką, słownikową wartość.\n"
        "- Nie dodawaj komentarzy ani wyjaśnień w wartościach parametrów.\n"
        "STRUKTURA OPISU HTML (ALLEGRO):\n"
        "1. TYLKO tagi: h1, h2, p, ul, ol, li, b, br. (ZAKAZ <i>, <div>, <span>, style).\n"
        "2. Pole 'description' musi być czystym tekstem HTML."
        f"{param_instruction}\n"
        f"Dane źródłowe: {source_desc[:3000]}"
    )
    
    ai_url = "https://gapli.com/api/product-customizer/ai/generate"
    ai_payload = {
        "provider_id": 1, "sku": sku, "platform": "allegro", "generation_type": "all", 
        "model": "gemini-3.5-flash", "product_data": {"name": current_name, "parameters": []},
        "custom_prompt": prompt
    }
    
    try:
        ai_resp = requests.post(ai_url, headers=HEADERS, json=ai_payload, timeout=60)
        if ai_resp.status_code != 200: 
            logger.error(f"    AI API error: {ai_resp.status_code}")
            return False
        
        ai_text = ai_resp.json().get("result", {}).get("description", "")
        
        # Parse JSON
        clean_text = ai_text.strip()
        if "```" in clean_text: clean_text = clean_text.split("```")[1].split("```")[0].strip()
        if clean_text.startswith("json"): clean_text = clean_text[4:].strip()
        ai_data = json.loads(clean_text)
        
        # Save
        save_payload = {
            "sku": sku, "scope": "user", "platform": "allegro",
            "custom_name": ai_data.get("name"),
            "custom_description": ai_data.get("description"),
            "custom_short_description": ai_data.get("short_description"),
            "custom_tags": ai_data.get("tags"),
            "custom_meta_title": ai_data.get("meta_title"),
            "custom_meta_description": ai_data.get("meta_description"),
            "custom_parameters": ai_data.get("parameters"),
            "is_active": True, "images_mode": "replace"
        }
        save_resp = requests.post("https://gapli.com/api/product-customizer/customizations", headers=HEADERS, json=save_payload)
        return save_resp.status_code in [200, 201]
    except Exception as e:
        logger.error(f"    Repair failed for {sku}: {e}")
        return False

def scan_and_repair():
    total_repaired = 0
    
    for acc_id in ACCOUNTS:
        logger.info(f"Scanning Account {acc_id} for sync errors using optimized filter...")
        page = 1
        while True:
            # OPTIMIZED FILTER: only fetch products with error status
            url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc_id}&allegro_sync_upload_status=error&limit=100&page={page}&mode=full"
            resp = requests.get(url, headers=HEADERS)
            if resp.status_code != 200: break
            
            data = resp.json()
            products = data.get("products", [])
            if not products: break
            
            logger.info(f"  Page {page}: Found {len(products)} error candidates...")
            
            for p in products:
                sku = p.get("sku")
                sync_status = p.get("allegro_sync_upload_status")
                error_msg = str(p.get("allegro_sync_upload_error_message") or "").lower()
                desc = str(p.get("allegro_offer_description") or "")
                
                # Detect missing parameters
                missing_params = []
                match = re.search(r"wymaganych: \[(.*?)\]", error_msg)
                if match:
                    missing_params = [x.strip() for x in match.group(1).split(",")]
                
                # We repair if it's a known fixable error (Parameters or HTML/JSON)
                is_fixable = (
                    (desc.strip().startswith("{") and '"description":' in desc) or 
                    "missing ending tag" in error_msg or 
                    "invalid tag" in error_msg or
                    "productvalidationexception" in error_msg or
                    "wszystkich parametrów wymaganych" in error_msg or
                    missing_params
                )
                
                    if is_fixable:
                        logger.info(f"Found fixable error: SKU {sku}")
                        # Use Proactive logic for every repair now
                        allegro_token = get_allegro_token()
                        if fix_sku_proactively(sku, acc_id, allegro_token):
                            logger.info(f"SUCCESS: Repaired SKU {sku}")
                            total_repaired += 1
                            time.sleep(5) # ANTI-RATE-LIMIT DELAY
                        else:
                            logger.warning(f"FAILED to repair SKU {sku}")
                            time.sleep(2)
            
            if page >= data.get("total_pages", 1): break
            page += 1
            if page > 100: break 
            
    logger.info(f"Repair cycle finished. Total products repaired: {total_repaired}")

if __name__ == "__main__":
    scan_and_repair()

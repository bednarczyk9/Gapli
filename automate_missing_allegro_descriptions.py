import requests
import json
import logging
import time
import pandas as pd
from datetime import datetime

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json"
}
ACCOUNT_ID = "61"

def get_data_maps():
    """
    Fetches all customizations and all products to build maps for:
    1. SKU -> Has Customization
    2. EAN -> List of SKUs that have customizations
    """
    logger.info("Fetching all customizations...")
    customized_skus = set()
    page = 1
    while True:
        url = f"https://gapli.com/api/product-customizer/customizations-list?page={page}&limit=100"
        resp = requests.get(url, headers=HEADERS)
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
    
    # Now fetch products to link EANs to SKUs
    # This might take a while if there are many products, so we'll fetch only enough to cover active ones
    logger.info("Fetching active products to build EAN map...")
    customized_eans = set()
    page = 1
    while True:
        # Fetching products in batches
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&status=ACTIVE&limit=100&page={page}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200: break
        data = resp.json()
        products = data.get("products", [])
        if not products: break
        
        for p in products:
            sku = p.get("sku")
            ean = p.get("gapli_product_global_unique_id") or p.get("ean")
            if sku in customized_skus and ean:
                customized_eans.add(ean)
                
        if page >= data.get("total_pages", 1) or page > 50: # Limit to first 5000 products for efficiency
            break
        page += 1
        
    logger.info(f"Identified {len(customized_eans)} EANs that already have customizations (corrected SKUs).")
    return customized_skus, customized_eans

def process_batch(limit=50):
    customized_skus, customized_eans = get_data_maps()
    
    logger.info(f"Scanning for candidates for 'Full Package' AI...")
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&status=ACTIVE&limit={limit}&mode=full"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        logger.error(f"Failed to fetch products: {resp.status_code}")
        return
        
    products = resp.json().get("products", [])
    
    candidates = []
    for p in products:
        sku = p.get("sku")
        ean = p.get("gapli_product_global_unique_id") or p.get("ean")
        
        # Check 1: SKU already customized
        if sku in customized_skus:
            continue
            
        # Check 2: EAN already customized (The "Poprawiony numer SKU" check)
        # If this product (EAN) exists elsewhere in the account with a customization, skip it.
        if ean and ean in customized_eans:
            logger.info(f"Skipping {sku}: Product with EAN {ean} already has a corrected/customized SKU.")
            continue
            
        offer_desc = p.get("allegro_offer_description")
        catalog_desc = p.get("allegro_catalog_description")
        gapli_desc = p.get("gapli_product_description")
        
        if not offer_desc and not catalog_desc and gapli_desc:
            candidates.append({
                "sku": sku,
                "ean": ean,
                "name": p.get("gapli_product_name") or p.get("allegro_catalog_product_name"),
                "description": gapli_desc,
                "parameters": p.get("gapli_product_attributes") or p.get("parameters") or []
            })
            
    logger.info(f"Found {len(candidates)} new candidates.")
    
    processed_results = []
    for i, candidate in enumerate(candidates):
        sku = candidate["sku"]
        logger.info(f"[{i+1}/{len(candidates)}] Processing {sku}...")
        
        result_entry = {"sku": sku, "ean": candidate["ean"], "status": "failed", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        try:
            # AI Prompt with JSON request
            prompt = (
                "Przygotuj PEŁNY PAKIET danych produktu (tytuł, opis HTML, krótki opis, tagi, parametry, SEO).\n"
                "ZWRÓĆ WYNIK W FORMIE JSON zawierającego klucze:\n"
                "name, description, short_description, tags, meta_title, meta_description, parameters (lista {name, value}).\n"
                f"Dane: {candidate['description'][:3000]}"
            )
            
            ai_url = "https://gapli.com/api/product-customizer/ai/generate"
            ai_payload = {
                "provider_id": 1, "sku": sku, "platform": "allegro", "generation_type": "all", 
                "model": "gemini-3.5-flash", "product_data": {"name": candidate["name"], "parameters": candidate["parameters"]},
                "custom_prompt": prompt
            }
            
            ai_resp = requests.post(ai_url, headers=HEADERS, json=ai_payload)
            if ai_resp.status_code != 200:
                result_entry["error"] = f"AI failed: {ai_resp.status_code}"
                processed_results.append(result_entry)
                continue
                
            ai_text = ai_resp.json().get("result", {}).get("description", "")
            
            # Parse JSON from AI
            ai_data = {}
            try:
                clean_text = ai_text.strip()
                if "```" in clean_text: clean_text = clean_text.split("```")[1].split("```")[0].strip()
                if clean_text.startswith("json"): clean_text = clean_text[4:].strip()
                ai_data = json.loads(clean_text)
            except:
                ai_data = {"description": ai_text}
            
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
            if save_resp.status_code in [200, 201]:
                result_entry["status"] = "success"
                # Add to customized_eans to avoid processing duplicates in the same run
                if candidate["ean"]: customized_eans.add(candidate["ean"])
            else:
                result_entry["error"] = f"Save failed: {save_resp.status_code}"
                
            time.sleep(1)
            
        except Exception as e:
            result_entry["error"] = str(e)
        
        processed_results.append(result_entry)

    if processed_results:
        pd.DataFrame(processed_results).to_excel(f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", index=False)

if __name__ == "__main__":
    process_batch(limit=20)

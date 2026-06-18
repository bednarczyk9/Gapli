import requests
import os
import base64
import json
import logging
from pipeline.repair_products_full import get_allegro_token, get_mandatory_params, rewrite_with_gemini

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

import sys
SKU = sys.argv[1] if len(sys.argv) > 1 else "ND05_B26167-M_4069161993367_30"
SHOP_NAME = "skarbiec_ofert" # Trying skarbiec_ofert first based on previous context, but user didn't specify. Let's just use skarbiec_ofert token for Allegro fetching.

def debug_sku():
    # 1. Fetch product from Gapli to find Category ID across all accounts just in case
    cat_id = None
    product_name = ""
    product_desc = ""
    
    for account_id in [116, 61, 64, 63, 8]:
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={account_id}&search={SKU}&mode=full"
        resp = requests.get(url, headers=GAPLI_HEADERS)
        if resp.status_code == 200:
            products = resp.json().get("products", [])
            for p in products:
                if p.get("sku") == SKU:
                    cat_id = p.get("allegro_catalog_category_id") or p.get("allegro_offer_category_id")
                    product_name = p.get("gapli_product_name") or p.get("allegro_catalog_product_name") or ""
                    product_desc = p.get("gapli_product_description") or p.get("allegro_catalog_description") or ""
                    logger.info(f"Found in account {account_id}. Category: {cat_id}")
                    break
            if cat_id: break
            
    if not cat_id:
        logger.error("Could not find product in Gapli.")
        return

    logger.info(f"Name: {product_name}")
    logger.info(f"Desc snippet: {product_desc[:100]}...")

    # 2. Fetch mandatory params from Allegro
    client_id = os.environ.get("skarbiec_client_id")
    client_secret = os.environ.get("skarbiec_client_secret")
    token = get_allegro_token(client_id, client_secret)
    
    if not token:
        logger.error("Failed to get Allegro token")
        return
        
    mandatory = get_mandatory_params(cat_id, token)
    logger.info(f"Mandatory Parameters from Allegro ({len(mandatory)}):")
    for m in mandatory:
        logger.info(f" - {m['name']} (ID: {m['id']}, Type: {m.get('type')})")
        if m.get('dictionary'):
            logger.info(f"   Dictionary: {m['dictionary'][:5]}...")
            
    # 3. Test Gemini
    logger.info("\n--- Running Gemini ---")
    ai_data = rewrite_with_gemini(product_name, product_desc, mandatory, [])
    
    if ai_data:
        logger.info("\n--- Raw Gemini Output (Parsed JSON) ---")
        logger.info(json.dumps(ai_data, indent=2, ensure_ascii=False))
        
        # 4. Show how our sanitization would process it
        cleaned_params = []
        for param in ai_data.get("parameters", []):
            if not isinstance(param, dict): continue
            cleaned_vals = []
            for v in param.get("values", []):
                if isinstance(v, dict):
                    cleaned_vals.append(str(v.get("value", v.get("name", list(v.values())[0] if v else ""))))
                else:
                    cleaned_vals.append(str(v))
            cleaned_params.append({
                "id": str(param.get("id", "")),
                "values": cleaned_vals
            })
            
        logger.info("\n--- Sanitized Parameters ---")
        logger.info(json.dumps(cleaned_params, indent=2, ensure_ascii=False))
    else:
        logger.error("Gemini returned None.")

if __name__ == "__main__":
    debug_sku()

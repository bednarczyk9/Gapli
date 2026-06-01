import requests
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

ACCOUNTS = ["61", "64", "116", "308", "146", "145", "142", "144"]

def fix_all_corrupted_products():
    total_fixed = 0
    
    for acc_id in ACCOUNTS:
        logger.info(f"Scanning Account {acc_id} for corrupted JSON descriptions...")
        page = 1
        while True:
            url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc_id}&status=ACTIVE&limit=100&page={page}&mode=full"
            resp = requests.get(url, headers=HEADERS)
            if resp.status_code != 200: break
            
            data = resp.json()
            products = data.get("products", [])
            if not products: break
            
            for p in products:
                sku = p.get("sku")
                # We check the gapli_product_description because that's what we usually override 
                # or what Gapli uses to sync the custom version.
                # However, the user said they saw the JSON in the Allegro sync error.
                
                found_json = False
                target_json = None
                
                # Check fields where AI data might have landed
                for field in ['allegro_offer_description', 'gapli_product_description']:
                    val = str(p.get(field) or "")
                    if val.strip().startswith("{") and '"description":' in val:
                        found_json = True
                        target_json = val
                        break
                
                if found_json:
                    logger.info(f"CORRUPTION DETECTED: SKU {sku} in Account {acc_id}")
                    try:
                        clean_text = target_json.strip()
                        if "```" in clean_text: clean_text = clean_text.split("```")[1].split("```")[0].strip()
                        if clean_text.startswith("json"): clean_text = clean_text[4:].strip()
                        
                        ai_data = json.loads(clean_text)
                        
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
                        save_payload = {k: v for k, v in save_payload.items() if v is not None}
                        
                        save_resp = requests.post("https://gapli.com/api/product-customizer/customizations", headers=HEADERS, json=save_payload)
                        if save_resp.status_code in [200, 201]:
                            logger.info(f"FIXED SKU {sku}")
                            total_fixed += 1
                        else:
                            logger.error(f"Failed to fix SKU {sku}: {save_resp.status_code}")
                    except Exception as e:
                        logger.error(f"Error repairing SKU {sku}: {e}")
            
            if page >= data.get("total_pages", 1): break
            page += 1
            if page > 10: break # Scan limit per account for safety
            
    logger.info(f"Finished. Total products fixed: {total_fixed}")

if __name__ == "__main__":
    fix_all_corrupted_products()

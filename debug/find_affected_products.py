import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = 116

BAD_DESCRIPTION_START = "Parasol Ogrodowy z Oświetleniem LED 300cm"

def find_affected_products():
    url = f"https://gapli.com/api/products-manager/allegro/products"
    params = {
        "konto_allegro_id": ACCOUNT_ID,
        "limit": 100,
        "page": 1,
        "mode": "full"
    }
    
    affected = []
    
    while True:
        logger.info(f"Checking page {params['page']}...")
        resp = requests.get(url, headers=GAPLI_HEADERS, params=params)
        if resp.status_code != 200:
            logger.error(f"Error fetching products: {resp.status_code}")
            break
            
        data = resp.json()
        products = data.get("products", [])
        if not products:
            break
            
        for p in products:
            sku = p.get("sku")
            if sku == "1053851_131":
                continue
                
            # Check custom description
            custom_desc = p.get("custom_description")
            # Also check regular description just in case it was pushed there
            offer_desc = p.get("allegro_offer_description")
            
            is_bad = False
            if custom_desc and BAD_DESCRIPTION_START in custom_desc:
                is_bad = True
                reason = "custom_description"
            elif offer_desc and BAD_DESCRIPTION_START in offer_desc:
                is_bad = True
                reason = "allegro_offer_description"
                
            if is_bad:
                logger.info(f"Found affected SKU: {sku} ({reason})")
                affected.append({
                    "sku": sku,
                    "reason": reason,
                    "gapli_description": p.get("gapli_product_description"),
                    "gapli_parameters": p.get("gapli_product_parameters") # Adjust if needed
                })
        
        params["page"] += 1
        if params["page"] > 50: # Safety break
            break
            
    return affected

if __name__ == "__main__":
    affected = find_affected_products()
    logger.info(f"Total affected products found: {len(affected)}")
    with open("affected_products.json", "w", encoding="utf-8") as f:
        json.dump(affected, f, indent=4, ensure_ascii=False)

import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = 61 # radosnydzieciak

SEARCH_STRING = "Parasol Ogrodowy"

def find_string_in_offers():
    url = f"https://gapli.com/api/products-manager/allegro/products"
    params = {
        "konto_allegro_id": ACCOUNT_ID,
        "limit": 100,
        "page": 1,
        "mode": "full"
    }
    
    found = []
    
    while True:
        logger.info(f"Checking page {params['page']}...")
        resp = requests.get(url, headers=GAPLI_HEADERS, params=params)
        if resp.status_code != 200:
            logger.error(f"Error: {resp.status_code}")
            break
            
        data = resp.json()
        products = data.get("products", [])
        if not products:
            break
            
        for p in products:
            sku = p.get("sku")
            if sku == "1053851_131":
                continue
                
            offer_desc = p.get("allegro_offer_description") or ""
            custom_desc = p.get("custom_description") or ""
            gapli_desc = p.get("gapli_product_description") or ""
            
            if SEARCH_STRING in offer_desc or SEARCH_STRING in custom_desc:
                logger.info(f"Found {SEARCH_STRING} in SKU {sku}")
                found.append({
                    "sku": sku,
                    "offer_desc_snippet": offer_desc[:100],
                    "custom_desc_snippet": custom_desc[:100],
                    "gapli_desc_snippet": gapli_desc[:100]
                })
        
        params["page"] += 1
        if params["page"] > 50: break
            
    return found

if __name__ == "__main__":
    found = find_string_in_offers()
    print(f"Total found: {len(found)}")
    print(json.dumps(found, indent=2, ensure_ascii=False))

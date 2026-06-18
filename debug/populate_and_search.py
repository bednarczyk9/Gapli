import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = 116

SEARCH_STR = "Lubisz spędzać czas na świeżym powietrzu"

def populate_and_search():
    affected = []
    page = 1
    while True:
        logger.info(f"Processing page {page}...")
        url = f"https://gapli.com/api/products-manager/allegro/products"
        params = {
            "konto_allegro_id": ACCOUNT_ID,
            "limit": 100,
            "page": page,
            "mode": "full" # This should trigger status fetch if not cached
        }
        
        try:
            resp = requests.get(url, headers=GAPLI_HEADERS, params=params, timeout=60)
            if resp.status_code != 200: break
            
            products = resp.json().get("products", [])
            if not products: break
            
            for p in products:
                sku = p.get("sku")
                if sku == "1053851_131": continue
                
                offer_desc = p.get("allegro_offer_description") or ""
                if SEARCH_STR in offer_desc:
                    logger.info(f"!!! FOUND AFFECTED SKU: {sku}")
                    affected.append(p)
            
        except Exception as e:
            logger.error(f"Error: {e}")
            break
            
        page += 1
        if page > 100: break
        
    return affected

if __name__ == "__main__":
    affected = populate_and_search()
    print(f"Total affected found: {len(affected)}")
    with open("affected_found_full.json", "w", encoding="utf-8") as f:
        json.dump(affected, f, indent=4, ensure_ascii=False)

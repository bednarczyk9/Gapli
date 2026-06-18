import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = 116

SEARCH_STRING = "Parasol Ogrodowy"

def fetch_page(page, limit=50):
    url = f"https://gapli.com/api/products-manager/allegro/products"
    params = {
        "konto_allegro_id": ACCOUNT_ID,
        "limit": limit,
        "page": page,
        "mode": "full"
    }
    
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=GAPLI_HEADERS, params=params, timeout=60)
            if resp.status_code == 200:
                return resp.json()
            logger.warning(f"Attempt {attempt+1} failed with status {resp.status_code}")
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed with error {e}")
        time.sleep(5)
    return None

def find_affected():
    found = []
    page = 1
    while True:
        logger.info(f"Fetching page {page}...")
        data = fetch_page(page)
        if not data:
            logger.error(f"Failed to fetch page {page}")
            break
            
        products = data.get("products", [])
        if not products:
            break
            
        for p in products:
            sku = p.get("sku")
            if sku == "1053851_131":
                continue
                
            offer_desc = p.get("allegro_offer_description") or ""
            
            if SEARCH_STRING in offer_desc:
                logger.info(f"Found affected SKU: {sku}")
                found.append(p)
                
        page += 1
        if page > 100: break
        
    return found

if __name__ == "__main__":
    affected = find_affected()
    logger.info(f"Total affected: {len(affected)}")
    with open("affected_products_details.json", "w", encoding="utf-8") as f:
        json.dump(affected, f, indent=4, ensure_ascii=False)

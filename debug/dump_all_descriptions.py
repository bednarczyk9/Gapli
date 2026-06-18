import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = 61

def fetch_all_descriptions():
    all_data = []
    page = 1
    while True:
        logger.info(f"Fetching page {page}...")
        url = f"https://gapli.com/api/products-manager/allegro/products"
        params = {
            "konto_allegro_id": ACCOUNT_ID,
            "limit": 100,
            "page": page,
            "mode": "full"
        }
        
        try:
            resp = requests.get(url, headers=GAPLI_HEADERS, params=params, timeout=60)
            if resp.status_code != 200:
                logger.error(f"Error: {resp.status_code}")
                break
            
            data = resp.json()
            products = data.get("products", [])
            if not products:
                break
                
            for p in products:
                all_data.append({
                    "sku": p.get("sku"),
                    "name": p.get("gapli_product_name"),
                    "offer_desc": p.get("allegro_offer_description"),
                    "custom_desc": p.get("custom_description"),
                    "gapli_desc": p.get("gapli_product_description")
                })
        except Exception as e:
            logger.error(f"Error on page {page}: {e}")
            break
            
        page += 1
        if page > 100: break # Max 10000 products
        
    return all_data

if __name__ == "__main__":
    all_data = fetch_all_descriptions()
    logger.info(f"Total products fetched: {len(all_data)}")
    with open("all_products_descriptions_61.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

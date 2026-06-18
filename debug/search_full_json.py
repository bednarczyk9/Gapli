import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = 116

SEARCH_STR = "Parasol"

def search_in_api_responses():
    affected = []
    page = 1
    while True:
        logger.info(f"Searching page {page}...")
        url = f"https://gapli.com/api/products-manager/allegro/products"
        params = {"konto_allegro_id": ACCOUNT_ID, "limit": 100, "page": page, "mode": "full"}
        
        resp = requests.get(url, headers=GAPLI_HEADERS, params=params)
        if resp.status_code != 200: break
        products = resp.json().get("products", [])
        if not products: break
        
        for p in products:
            sku = p.get("sku")
            if sku == "1053851_131": continue
            
            # Check all text fields
            s = json.dumps(p)
            if SEARCH_STR in s:
                logger.info(f"!!! FOUND SEARCH_STR IN PRODUCT {sku}")
                affected.append(p)
                
        page += 1
        if page > 50: break
    return affected

if __name__ == "__main__":
    affected = search_in_api_responses()
    print(f"Total found: {len(affected)}")
    with open("found_by_full_json_search.json", "w", encoding="utf-8") as f:
        json.dump(affected, f, indent=4, ensure_ascii=False)

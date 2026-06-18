import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

ACCOUNTS = [116, 61, 64, 63]
SEARCH_STR = "Parasol"

def global_search():
    found = []
    for acc_id in ACCOUNTS:
        logger.info(f"Searching in account {acc_id}...")
        url = f"https://gapli.com/api/products-manager/allegro/products"
        page = 1
        while True:
            params = {
                "konto_allegro_id": acc_id,
                "limit": 100,
                "page": page,
                "mode": "full"
            }
            try:
                resp = requests.get(url, headers=GAPLI_HEADERS, params=params, timeout=30)
                if resp.status_code != 200: break
                products = resp.json().get("products", [])
                if not products: break
                
                for p in products:
                    sku = p.get("sku")
                    if sku == "1053851_131": continue
                    
                    custom_desc = p.get("custom_description") or ""
                    offer_desc = p.get("allegro_offer_description") or ""
                    
                    if SEARCH_STR in custom_desc or SEARCH_STR in offer_desc:
                        logger.info(f"Found match in account {acc_id}, SKU {sku}")
                        found.append({
                            "account_id": acc_id,
                            "sku": sku,
                            "name": p.get("gapli_product_name")
                        })
                page += 1
                if page > 20: break # Sample
            except Exception:
                break
    return found

if __name__ == "__main__":
    found = global_search()
    print(f"Total found: {len(found)}")
    print(json.dumps(found, indent=2))

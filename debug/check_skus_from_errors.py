import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = 116

with open("error_skus.json", "r") as f:
    skus = json.load(f)

search_str = "Parasol Ogrodowy"

def check_skus():
    affected = []
    for sku in skus:
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={sku}&mode=full"
        try:
            resp = requests.get(url, headers=GAPLI_HEADERS, timeout=30)
            if resp.status_code == 200:
                products = resp.json().get("products", [])
                for p in products:
                    if p.get("sku") == sku:
                        offer_desc = p.get("allegro_offer_description") or ""
                        if search_str in offer_desc:
                            logger.info(f"Found affected SKU in error list: {sku}")
                            affected.append(p)
        except Exception as e:
            logger.error(f"Error checking {sku}: {e}")
            
    return affected

if __name__ == "__main__":
    affected = check_skus()
    print(f"Total affected found from error list: {len(affected)}")
    with open("affected_from_errors.json", "w", encoding="utf-8") as f:
        json.dump(affected, f, indent=4, ensure_ascii=False)

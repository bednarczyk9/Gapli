import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = 116

def find_failed_syncs():
    url = f"https://gapli.com/api/products-manager/allegro/products"
    page = 1
    failed = []
    while True:
        params = {"konto_allegro_id": ACCOUNT_ID, "limit": 100, "page": page, "mode": "full"}
        resp = requests.get(url, headers=GAPLI_HEADERS, params=params)
        if resp.status_code != 200: break
        products = resp.json().get("products", [])
        if not products: break
        
        for p in products:
            if p.get("allegro_sync_upload_status") == "failed":
                failed.append({
                    "sku": p.get("sku"),
                    "error": p.get("allegro_sync_upload_error_message"),
                    "offer_id": p.get("allegro_offer_id")
                })
        page += 1
        if page > 50: break
    return failed

if __name__ == "__main__":
    failed = find_failed_syncs()
    print(f"Total failed syncs: {len(failed)}")
    print(json.dumps(failed[:20], indent=2))

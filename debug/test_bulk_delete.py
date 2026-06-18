import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GAPLI_API_KEY = "gapli_ba90f561bf78bf55652e21b5ed33400b7551219e"
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}
ACCOUNT_ID = "116"

def test_bulk_action(action, skus):
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    body = {
        "action": action,
        "account_id": ACCOUNT_ID,
        "product_skus": skus
    }
    logger.info(f"Attempting action '{action}' for {len(skus)} SKUs...")
    resp = requests.post(url, headers=HEADERS, json=body)
    logger.info(f"Response: {resp.status_code} {resp.text}")
    return resp.status_code

if __name__ == "__main__":
    # Fetch some DRAFT SKUs first
    h_jwt = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"}
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&status=DRAFT&limit=5"
    r = requests.get(url, headers=h_jwt)
    if r.status_code == 200:
        skus = [p['sku'] for p in r.json().get('products', [])]
        if skus:
            logger.info(f"Testing with SKUs: {skus}")
            # Try 'end' (common for finishing offers)
            test_bulk_action("end", skus)
            time.sleep(2)
            # Try 'delete'
            test_bulk_action("delete", skus)
            time.sleep(2)
            # Try 'remove'
            test_bulk_action("remove", skus)
        else:
            logger.warning("No DRAFT SKUs found to test.")
    else:
        logger.error(f"Failed to fetch DRAFTs: {r.status_code}")

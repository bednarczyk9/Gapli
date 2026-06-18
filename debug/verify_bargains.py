import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Accept": "application/json"}
ACCOUNT_ID = "116"

SKUS = ["107360_41", "104053BRNS003_222", "4225A_131", "HG83ETUI_131", "A0005656BLKS534_222"]

def verify_specific_skus():
    for sku in SKUS:
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={sku}&mode=full"
        resp = requests.get(url, headers=GAPLI_HEADERS)
        if resp.status_code == 200:
            products = resp.json().get("products", [])
            if products:
                p = products[0]
                offer_id = p.get('allegro_offer_id')
                status = p.get('allegro_offer_status')
                sync_msg = p.get('allegro_sync_upload_error_message') or p.get('allegro_sync_publication_error_message')
                logger.info(f"SKU: {sku} | OfferID: {offer_id} | Status: {status} | SyncMsg: {sync_msg}")
            else:
                logger.warning(f"SKU: {sku} not found for account {ACCOUNT_ID}")
        else:
            logger.error(f"Failed to fetch {sku}: {resp.status_code}")

GAPLI_API_KEY = "gapli_ba90f561bf78bf55652e21b5ed33400b7551219e"
GAPLI_INTEGRATIONS_HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}

def send_top_bargains():
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    body = {
        "action": "send",
        "account_id": ACCOUNT_ID,
        "product_skus": SKUS,
        "price_range": {"min": 50, "max": 50000}
    }
    logger.info(f"Explicitly sending {SKUS} to AlejaOkazji...")
    resp = requests.post(url, headers=GAPLI_INTEGRATIONS_HEADERS, json=body)
    if resp.status_code == 200:
        logger.info(f"  Response: {resp.json().get('message')}")
    else:
        logger.error(f"  Failed: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    verify_specific_skus()
    send_top_bargains()

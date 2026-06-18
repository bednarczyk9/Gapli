import requests
import os
import json
import time

# Using AlejaOkazji API key for Gapli (known working for general listing actions)
GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
GAPLI_HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}

ACCOUNT_ID = "63" # skarbiec_ofert
SKU = "1053851_131"

def force_fresh_send():
    print(f"Triggering fresh SEND for SKU {SKU} on account {ACCOUNT_ID}...")
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    
    # We use 'send' but since it has no Offer ID (it was reset), 
    # Gapli should try to POST it as a new offer.
    payload = {
        "action": "send",
        "account_id": ACCOUNT_ID,
        "product_skus": [SKU]
    }
    
    resp = requests.post(url, headers=GAPLI_HEADERS, json=payload)
    print(f"Response ({resp.status_code}): {resp.text}")
    
    # Check status after a few seconds
    time.sleep(3)
    check_url = f"https://gapli.com/api/v1/integrations/marketplace/listing"
    check_payload = {
        "action": "get-status",
        "account_id": ACCOUNT_ID,
        "product_skus": [SKU]
    }
    check_resp = requests.post(check_url, headers=GAPLI_HEADERS, json=check_payload)
    print("\nNew Status:")
    print(check_resp.text)

if __name__ == "__main__":
    force_fresh_send()

import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}
SKU = "1053851_131"
ACCOUNT_ID = "116"

def try_advanced_send():
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    
    # Try different field names for forcing update
    variants = [
        {"force": True},
        {"force_update": True},
        {"mode": "resend"},
        {"mode": "update"},
        {"duplicates_mode": "resend"},
        {"handle_duplicates": "resend"},
        {"duplicate_handling": "resend"}
    ]
    
    for var in variants:
        print(f"Trying variant: {var}")
        body = {
            "action": "send",
            "account_id": ACCOUNT_ID,
            "product_skus": [SKU],
            "price_range": {"min": 50, "max": 50000}
        }
        body.update(var)
        
        resp = requests.post(url, headers=HEADERS, json=body)
        print(f"  Response ({resp.status_code}): {resp.text[:200]}")

if __name__ == "__main__":
    try_advanced_send()

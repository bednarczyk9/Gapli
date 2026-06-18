import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}
SKU = "1053851_131"
ACCOUNT_ID = "116"

def try_resend_action():
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    
    # Try different action names
    actions = ["send", "resend", "update", "sync", "force_send"]
    
    for action in actions:
        print(f"Trying action: {action}")
        body = {
            "action": action,
            "account_id": ACCOUNT_ID,
            "product_skus": [SKU],
            "price_range": {"min": 50, "max": 50000}
        }
        
        resp = requests.post(url, headers=HEADERS, json=body)
        print(f"  Response ({resp.status_code}): {resp.text[:200]}")

if __name__ == "__main__":
    try_resend_action()

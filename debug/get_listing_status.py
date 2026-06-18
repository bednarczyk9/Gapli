import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}
SKU = "1053851_131"
ACCOUNT_ID = "116"

def get_status():
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    body = {
        "action": "get-status",
        "account_id": ACCOUNT_ID,
        "product_skus": [SKU]
    }
    
    resp = requests.post(url, headers=HEADERS, json=body)
    print(f"Response ({resp.status_code}): {resp.text}")

if __name__ == "__main__":
    get_status()

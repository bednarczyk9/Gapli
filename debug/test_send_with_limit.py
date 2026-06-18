import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"}

def try_send_with_limit():
    sku = "ND28_13110_PA_JT5007_ZIE_30"
    
    body = {
        "action": "send",
        "account_id": "116",
        "product_skus": [sku],
        "limit": 200000,
        "products_limit": 200000,
        "max_products": 200000
    }
    
    print(f"Attempting to add SKU {sku} with limit parameters...")
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    resp = requests.post(url, headers=HEADERS, json=body)
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.text}")

if __name__ == "__main__":
    try_send_with_limit()

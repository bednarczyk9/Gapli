import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"}

def try_update_limit():
    url = "https://gapli.com/api/v1/integrations/marketplace/accounts"
    
    # We try to update account 116 (AlejaOkazji)
    body = {
        "id": "116",
        "action": "update",
        "products_limit": 200000,
        "max_products": 200000,
        "limit": 200000
    }
    
    print(f"POST {url} with body: {json.dumps(body)}")
    resp = requests.post(url, headers=HEADERS, json=body)
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.text[:500]}")

if __name__ == "__main__":
    try_update_limit()

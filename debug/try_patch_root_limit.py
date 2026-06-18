import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"}

def try_patch_root():
    url = "https://gapli.com/api/v1/integrations/marketplace/accounts"
    
    body = {
        "id": "116",
        "products_limit": 200000,
        "limit": 200000,
        "max_products": 200000
    }
    
    print(f"PATCH {url} with body: {json.dumps(body)}")
    resp = requests.patch(url, headers=HEADERS, json=body)
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.text[:500]}")

if __name__ == "__main__":
    try_patch_root()

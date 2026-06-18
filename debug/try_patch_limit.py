import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"}

def try_patch():
    account_id = 116
    url = f"https://gapli.com/api/v1/integrations/marketplace/accounts/{account_id}"
    
    # Body with the new limit
    body = {
        "limit": 200000,
        "products_limit": 200000,
        "max_products": 200000
    }
    
    print(f"PATCH {url}")
    resp = requests.patch(url, headers=HEADERS, json=body)
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.text[:500]}")
    
    # Try store update too
    store_id = 308
    store_url = f"https://gapli.com/api/v1/integrations/stores/{store_id}"
    print(f"PATCH {store_url}")
    resp_s = requests.patch(store_url, headers=HEADERS, json=body)
    print(f"  Status: {resp_s.status_code}")
    print(f"  Response: {resp_s.text[:500]}")

if __name__ == "__main__":
    try_patch()

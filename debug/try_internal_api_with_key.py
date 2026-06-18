import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def try_internal_api():
    urls = [
        "https://gapli.com/api/store-manager/stores",
        "https://gapli.com/api/products-manager/allegro/products/stats",
        "https://gapli.com/api/account-manager/accounts",
    ]
    
    for url in urls:
        print(f"GET {url}")
        resp = requests.get(url, headers=HEADERS)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
             print(f"  Response: {json.dumps(resp.json(), indent=2)[:500]}...")
        else:
             print(f"  Error: {resp.text[:200]}")

if __name__ == "__main__":
    try_internal_api()

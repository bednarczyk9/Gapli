import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def try_internal_acc():
    acc_id = 116
    urls = [
        f"https://gapli.com/api/products-manager/allegro/accounts/{acc_id}",
        f"https://gapli.com/api/products-manager/allegro/accounts",
        f"https://gapli.com/api/account-manager/accounts/{acc_id}",
        f"https://gapli.com/api/store-manager/stores/308",
    ]
    
    for url in urls:
        print(f"GET {url}")
        resp = requests.get(url, headers=HEADERS)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Response: {json.dumps(resp.json(), indent=2)[:500]}...")

if __name__ == "__main__":
    try_internal_acc()

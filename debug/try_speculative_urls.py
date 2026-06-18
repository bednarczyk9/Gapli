import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def try_urls():
    store_id = 308
    acc_id = 116
    
    urls = [
        f"https://gapli.com/api/v1/integrations/stores/{store_id}/settings",
        f"https://gapli.com/api/v1/integrations/stores/{store_id}/limits",
        f"https://gapli.com/api/v1/integrations/marketplace/accounts/{acc_id}/settings",
        f"https://gapli.com/api/v1/integrations/marketplace/accounts/{acc_id}/limits",
        f"https://gapli.com/api/v1/integrations/marketplace/accounts/{acc_id}/quota",
        f"https://gapli.com/api/v1/stores/{store_id}",
        f"https://gapli.com/api/v1/stores/{store_id}/settings",
    ]
    
    for url in urls:
        print(f"GET {url}")
        resp = requests.get(url, headers=HEADERS)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Response: {json.dumps(resp.json(), indent=2)}")

if __name__ == "__main__":
    try_urls()

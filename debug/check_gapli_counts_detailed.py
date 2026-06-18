import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def list_more():
    urls = [
        "https://gapli.com/api/v1/integrations/marketplace/products?account_id=116&limit=1&status=active",
        "https://gapli.com/api/v1/integrations/marketplace/products?account_id=116&limit=1&status=pending",
        "https://gapli.com/api/v1/integrations/marketplace/products?account_id=116&limit=1&status=error",
        "https://gapli.com/api/v1/integrations/marketplace/products?account_id=116&limit=1&status=draft",
        "https://gapli.com/api/v1/integrations/marketplace/products?account_id=116&limit=1&status=ended",
    ]
    for url in urls:
        print(f"GET {url}")
        resp = requests.get(url, headers=HEADERS)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"  Total: {data.get('pagination', {}).get('total')}")

if __name__ == "__main__":
    list_more()

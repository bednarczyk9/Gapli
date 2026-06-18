import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}
ACCOUNT_ID = 116

def check_offset_10000():
    url = f"https://gapli.com/api/v1/integrations/marketplace/products?account_id={ACCOUNT_ID}&limit=10&offset=10000"
    resp = requests.get(url, headers=HEADERS)
    print(f"Status at 10000: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Products at 10000: {len(data.get('products', []))}")
        print(f"Total in pagination: {data.get('pagination', {}).get('total')}")
        print(f"Has more: {data.get('pagination', {}).get('has_more')}")
        
    url_20000 = f"https://gapli.com/api/v1/integrations/marketplace/products?account_id={ACCOUNT_ID}&limit=10&offset=20000"
    resp_20000 = requests.get(url_20000, headers=HEADERS)
    print(f"Status at 20000: {resp_20000.status_code}")
    if resp_20000.status_code == 200:
        data = resp_20000.json()
        print(f"Products at 20000: {len(data.get('products', []))}")

if __name__ == "__main__":
    check_offset_10000()

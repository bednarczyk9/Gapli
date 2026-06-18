import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def fetch_sample():
    account_id = 116
    print(f"Fetching sample products for account {account_id}...")
    
    url = f"https://gapli.com/api/v1/integrations/marketplace/products?account_id={account_id}&limit=10"
    resp = requests.get(url, headers=HEADERS)
    
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        for p in products:
            print(f"SKU: {p.get('sku')}, Allegro ID: {p.get('allegro_offer_id')}, Status: {p.get('status')}")
    else:
        print(f"Error: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    fetch_sample()

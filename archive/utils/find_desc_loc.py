import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def find_description_location():
    sku = "82902_232"
    
    # 1. Check products-manager details
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id=61&search={sku}&mode=full"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("products"):
            p = data["products"][0]
            print(f"Products-Manager Description: {str(p.get('allegro_offer_description'))[:200]}")
    
    # 2. Check ALL customizations (without limit or specific filters)
    url = "https://gapli.com/api/product-customizer/customizations"
    # Try with account 64 (ID next to hit_bazar in screenshot)
    for params in [{"sku": sku, "account_id": "64"}, {"sku": sku, "store_id": "142"}, {"sku": sku}]:
        r = requests.get(url, headers=HEADERS, params=params)
        print(f"Testing {url} with {params}: {r.status_code}")
        if r.status_code == 200:
            d = r.json()
            if d.get("data"):
                 print(f"MATCH FOUND in 'data'! Description: {str(d['data'].get('custom_description'))[:200]}")
            else:
                 print(f"No 'data' in response for {params}")

    # 6. Scan for any products with JSON in description
    accounts = ["61", "64", "116", "308", "146", "145", "142", "144"]
    for acc_id in accounts:
        print(f"Scanning Account {acc_id} for corrupted descriptions...")
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc_id}&status=ACTIVE&limit=100&mode=full"
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            d = r.json()
            prods = d.get("products", [])
            for p in prods:
                # Check both allegro_offer_description and gapli_product_description
                for field in ['allegro_offer_description', 'gapli_product_description']:
                    desc = str(p.get(field) or "")
                    if desc.strip().startswith("{") and '"description":' in desc:
                        print(f"!!! CORRUPTION DETECTED in Account {acc_id}, SKU {p.get('sku')}, Field {field} !!!")
                        print(f"Desc snippet: {desc[:100]}")

if __name__ == "__main__":
    find_description_location()

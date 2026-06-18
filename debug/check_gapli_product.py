import requests
import os
import json

# Hardcoded token from repair_aleja_okazji.py
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = "61" # AlejaOkazji
SKU = "12014_88"

def check_gapli_product():
    print(f"Checking Gapli product: {SKU}")
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        if products:
            p = products[0]
            print(f"Found product: {p.get('gapli_product_name')}")
            print(f"Sync status: {p.get('allegro_sync_status')}")
            print(f"Upload error: {p.get('allegro_sync_upload_error_message')}")
            print(f"Offer ID: {p.get('allegro_offer_id')}")
            print(f"Draft ID: {p.get('allegro_draft_id')}")
            print(f"Integration status: {p.get('allegro_integration_status')}")
            
            # Print full product data to see if anything else is relevant
            print("\nFull product data:")
            print(json.dumps(p, indent=2, ensure_ascii=False))
            
            return p
        else:
            print("Product not found in Gapli.")
    else:
        print(f"Failed to fetch product from Gapli: {resp.status_code} {resp.text}")
    return None

if __name__ == "__main__":
    check_gapli_product()

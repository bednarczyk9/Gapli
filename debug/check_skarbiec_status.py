import requests
import os
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = "63" # skarbiec_ofert
SKU = "1053851_131"

def check_skarbiec_status():
    print(f"Checking SKU {SKU} on account {ACCOUNT_ID} (skarbiec_ofert)...")
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        if products:
            p = products[0]
            print(f"Status: {p.get('allegro_sync_status')}")
            print(f"Error Code: {p.get('allegro_sync_upload_error_code')}")
            print(f"Error Message: {p.get('allegro_sync_upload_error_message')}")
            print(f"Offer ID: {p.get('allegro_offer_id')}")
            
            # Print full response if there's one
            api_resp = p.get('allegro_api_response')
            if api_resp:
                print("\nAllegro API Response:")
                print(json.dumps(api_resp, indent=2, ensure_ascii=False))
        else:
            print("Product not found on this account in Gapli.")
    else:
        print(f"Failed to fetch: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    check_skarbiec_status()

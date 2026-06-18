import requests
import os
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def check_other_accounts():
    accounts = [
        {"id": "61", "name": "radosnydzieciak"},
        {"id": "64", "name": "hit_bazar"},
        {"id": "116", "name": "AlejaOkazji"}
    ]
    
    for acc in accounts:
        print(f"\nChecking SKU {SKU} on account {acc['name']} (ID {acc['id']})...")
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc['id']}&search={SKU}&mode=full"
        resp = requests.get(url, headers=GAPLI_HEADERS)
        
        if resp.status_code == 200:
            products = resp.json().get("products", [])
            if products:
                p = products[0]
                print(f"  Status: {p.get('allegro_sync_status')}")
                print(f"  Upload Error: {p.get('allegro_sync_upload_error_message')}")
                print(f"  Offer ID: {p.get('allegro_offer_id')}")
            else:
                print("  Product not found on this account.")
        else:
            print(f"  Failed to fetch: {resp.status_code}")

if __name__ == "__main__":
    check_other_accounts()

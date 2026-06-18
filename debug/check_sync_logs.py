import requests
import os
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = "63" # skarbiec_ofert
SKU = "12014_88"

def check_sync_logs():
    print(f"Checking full status and history for {SKU}...")
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        if products:
            p = products[0]
            print(f"Status: {p.get('allegro_sync_status')}")
            print(f"Sync Stock Status: {p.get('allegro_sync_stock_status')}")
            print(f"Sync Price Status: {p.get('allegro_sync_price_status')}")
            
            history = p.get('gapli_sync_history')
            if history:
                print("\nSync History:")
                print(json.dumps(history, indent=2, ensure_ascii=False))
            
            ops = p.get('sync_operation_history')
            if ops:
                print("\nOperation History:")
                print(json.dumps(ops, indent=2, ensure_ascii=False))
        else:
            print("Not found.")

if __name__ == "__main__":
    check_sync_logs()

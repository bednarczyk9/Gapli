import requests
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def find_and_debug():
    sku = "1004260-660_150"
    accounts = ["61", "64", "116", "308", "146", "145", "142", "144"]
    
    found_acc = None
    for acc in accounts:
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc}&search={sku}&mode=full"
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            prods = r.json().get("products", [])
            if prods:
                print(f"SKU {sku} FOUND in Account {acc}")
                found_acc = acc
                break
    
    if found_acc:
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={found_acc}&search={sku}&mode=full"
        r = requests.get(url, headers=HEADERS)
        p = r.json()["products"][0]
        print(f"Product Status: {p.get('allegro_sync_upload_status')}")
        print(f"Error Message: {p.get('allegro_sync_upload_error_message')}")

if __name__ == "__main__":
    find_and_debug()

import requests
import os
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
EAN = "5902431053851"

def check_ean_duplicates():
    print(f"Checking for EAN: {EAN}")
    url = f"https://gapli.com/api/products-manager/allegro/products?search={EAN}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        print(f"Found {len(products)} products with this EAN.")
        for p in products:
            print(f"SKU: {p.get('sku')} | Account: {p.get('konto_allegro_id')} | Status: {p.get('allegro_offer_status')} | ID: {p.get('allegro_offer_id')}")
    else:
        print(f"Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    check_ean_duplicates()

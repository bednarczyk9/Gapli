import requests
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def find_ean_116():
    sku = "12827_166"
    url = f"https://gapli.com/api/products-manager/allegro/products?account_id=116&search={sku}&mode=full"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("products"):
            p = data["products"][0]
            ean = p.get('gapli_product_global_unique_id') or p.get('ean')
            print(f"SKU: {sku}, EAN: {ean}")
            return ean
    return None

if __name__ == "__main__":
    find_ean_116()

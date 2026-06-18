import requests
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"

def check():
    url = 'https://gapli.com/api/products-manager/allegro/products?status=ACTIVE&limit=100&mode=full'
    resp = requests.get(url, headers={'Authorization': GAPLI_TOKEN})
    data = resp.json()
    found = False
    for p in data.get("products", []):
        if p.get('allegro_catalog_category_id') == '258919':
            print(f"SKU: {p['sku']}")
            print(f"Params: {json.dumps(p['allegro_catalog_parameters'], indent=2, ensure_ascii=False)}")
            found = True
    if not found:
        print("No active products in category 258919 found in the last 100 items.")

if __name__ == "__main__":
    check()

import requests
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

def check():
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id=116&limit=1&page=1&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    p = resp.json().get('products', [])[0]
    
    print("Catalog Parameters:", p.get("allegro_catalog_parameters"))
    print("Gapli Parameters:", p.get("gapli_product_parameters"))

if __name__ == "__main__":
    check()

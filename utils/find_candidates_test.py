import requests
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def find_missing_description_product():
    page = 1
    while True:
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id=61&status=ACTIVE&limit=100&page={page}&mode=full"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200: break
        data = resp.json()
        products = data.get("products", [])
        if not products: break
        
        for p in products:
            offer_desc = p.get("allegro_offer_description")
            catalog_desc = p.get("allegro_catalog_description")
            gapli_desc = p.get("gapli_product_description")
            ean = p.get("gapli_product_global_unique_id") or p.get("ean")
            
            if not offer_desc and not catalog_desc and not gapli_desc and ean:
                print(f"Found candidate: SKU={p.get('sku')}, EAN={ean}, Name={p.get('gapli_product_name')}")
                # return p
                
        if page >= data.get("total_pages", 1): break
        page += 1
        if page > 5: break # Only check first 500 products
    return None

if __name__ == "__main__":
    find_missing_description_product()

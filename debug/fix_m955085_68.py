import requests
import json
import os

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN}
SKU = "M955085_68"

def check_product():
    # 1. Fetch product data from Gapli
    url = f"https://gapli.com/api/products-manager/allegro/products?search={SKU}&mode=full"
    r = requests.get(url, headers=GAPLI_HEADERS)
    if r.status_code != 200:
        print(f"Error fetching product: {r.status_code}")
        return
    
    products = r.json().get('products', [])
    if not products:
        print("Product not found.")
        return
    
    p = products[0]
    print(f"SKU: {p['sku']}")
    print(f"Name: {p['gapli_product_name']}")
    print(f"Status: {p['allegro_sync_upload_status']}")
    print(f"Description: {p.get('allegro_offer_description')}")
    print(f"Gapli Desc: {p.get('gapli_product_description', 'EMPTY')[:100]}...")
    print(f"Error: {p['allegro_sync_upload_error_message']}")
    print(f"Category ID: {p['allegro_catalog_category_id']}")
    
    print("\nCatalog Parameters:")
    print(json.dumps(p.get('allegro_catalog_parameters', []), indent=2, ensure_ascii=False))
    
    # 2. Fetch customization
    cust_url = f"https://gapli.com/api/product-customizer/customizations/{SKU}?scope=user&platform=allegro"
    r_cust = requests.get(cust_url, headers=GAPLI_HEADERS)
    if r_cust.status_code == 200:
        cust = r_cust.json()
        print("\nExisting Customization:")
        print(json.dumps(cust.get('custom_parameters', {}), indent=2, ensure_ascii=False))
    else:
        print(f"\nNo customization found or error: {r_cust.status_code}")

if __name__ == "__main__":
    check_product()

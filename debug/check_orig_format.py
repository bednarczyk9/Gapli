import requests
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = "ND05_B26167-M_4069161993367_30"

for acc in [63]: # It is active here
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc}&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS).json()
    for p in resp.get("products", []):
        if p["sku"] == SKU:
            print(f"Gapli Parameters (Orig) in {acc}:")
            print(p.get("gapli_product_parameters"))
            
            print(f"Gapli Attributes (Orig) in {acc}:")
            print(p.get("gapli_product_attributes"))
            
            print(f"Allegro Catalog Parameters in {acc}:")
            print(p.get("allegro_catalog_parameters"))

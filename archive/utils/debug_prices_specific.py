import requests
import os
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
headers = {"Authorization": TOKEN}

def check_prices(sku):
    url = "https://gapli.com/api/products-manager/allegro/products"
    params = {"search": sku, "mode": "full"}
    resp = requests.get(url, params=params, headers=headers)
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        print(f"\n--- WYNIKI DLA SKU: {sku} ---")
        for p in products:
            print(f"Sklep: {p.get('allegro_login')} | Hurtownia (ID): {p.get('parser_id')}")
            print(f"  - gapli_product_sale_price_brutto (Cena Gapli): {p.get('gapli_product_sale_price_brutto')}")
            print(f"  - allegro_offer_price_final_brutto (Cena Allegro): {p.get('allegro_offer_price_final_brutto')}")
            print(f"  - gapli_product_sale_brutto_promo_price: {p.get('gapli_product_sale_brutto_promo_price')}")
            print("-" * 50)
    else:
        print(f"Błąd dla {sku}: {resp.status_code}")

if __name__ == "__main__":
    check_prices("180800_134")
    check_prices("700_152")

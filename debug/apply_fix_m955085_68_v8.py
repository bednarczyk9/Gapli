import requests
import time
import json
import os

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
GAPLI_API_KEY = "gapli_ba90f561bf78bf55652e21b5ed33400b7551219e"

def update_customization(sku, store_id=None):
    print(f"Updating customization for SKU {sku} (Store: {store_id})...")
    payload = {
        "sku": sku, "scope": "user", "platform": "allegro",
        "store_id": store_id,
        "custom_parameters": {
            "Kolor": "szary",
            "Rozmiar": "L/XL",
            "EAN (GTIN)": "5904726003527",
            "Marka": "bez marki",
            "Nazwa koloru producenta": "Grafitowy",
            "Kod producenta": "157721"
        },
        "is_active": True, "images_mode": "replace"
    }
    resp = requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=payload)
    return resp.status_code in [200, 201]

def fix():
    target_skus = ["M955085_68", "157721_68"]
    
    for sku in target_skus:
        update_customization(sku, None)
        # Apply to known store IDs too
        for s_id in ["308", "63", "142", "144", "145"]:
            update_customization(sku, s_id)

    # Nuke and Resend for the specific SKU
    url = f"https://gapli.com/api/products-manager/allegro/products?search=M955085_68&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    products = resp.json().get("products", [])
    
    for p in products:
        p_id = p['id']
        acc_id = p['konto_allegro_id']
        if p.get("gapli_product_stock_quantity", 0) > 0:
            print(f"Nuking and re-sending Acc {acc_id}...")
            # Use permanent-delete
            requests.delete("https://gapli.com/api/products-manager/allegro/permanent-delete", 
                           headers=GAPLI_HEADERS, 
                           json={"mode": "selected", "product_ids": [{"id": str(p_id), "konto_allegro_id": str(acc_id)}]})
            time.sleep(5)
            # Use listing send
            requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", 
                         headers={"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"},
                         json={"action": "send", "account_id": str(acc_id), "product_skus": ["M955085_68"], "force_update": True})
            time.sleep(2)

if __name__ == "__main__":
    fix()

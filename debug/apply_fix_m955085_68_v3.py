import requests
import time
import json
import os

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
GAPLI_API_KEY = "gapli_ba90f561bf78bf55652e21b5ed33400b7551219e"
SKU = "M955085_68"

def update_customization(store_id=None):
    print(f"Updating customization for SKU {SKU} (Store: {store_id})...")
    payload = {
        "sku": SKU, "scope": "user", "platform": "allegro",
        "store_id": store_id,
        "custom_parameters": {
            "Stan": "Nowy",
            "11323": "Nowy", # Stan ID
            "Kolor": "szary",
            "249512": "szary", # Kolor ID
            "Odcień": "grafitowy",
            "249513": "grafitowy", # Odcień ID
            "Marka": "bez marki",
            "248811": "bez marki", # Marka ID
            "Rozmiar": "L/XL",
            "54": "L/XL", # Rozmiar ID
            "EAN (GTIN)": "5904726003527",
            "225693": "5904726003527", # EAN ID
            "Nazwa koloru producenta": "Grafit"
        },
        "is_active": True, "images_mode": "replace"
    }
    resp = requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=payload)
    print(f"Customization update status: {resp.status_code}")
    return resp.status_code in [200, 201]

def permanent_delete(product_id, account_id):
    print(f"Deleting product ID {product_id} from account {account_id}...")
    del_url = "https://gapli.com/api/products-manager/allegro/permanent-delete"
    payload = {
        "mode": "selected",
        "product_ids": [{"id": str(product_id), "konto_allegro_id": str(account_id)}]
    }
    resp = requests.delete(del_url, headers=GAPLI_HEADERS, json=payload)
    print(f"Delete status: {resp.status_code}")
    return resp.status_code == 200

def send_to_allegro(sku, account_id):
    print(f"Sending SKU {sku} to account {account_id}...")
    send_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    send_headers = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}
    payload = {"action": "send", "account_id": str(account_id), "product_skus": [sku], "force_update": True}
    resp = requests.post(send_url, headers=send_headers, json=payload)
    print(f"Send status: {resp.status_code} {resp.text}")
    return resp.status_code == 200

def fix():
    url = f"https://gapli.com/api/products-manager/allegro/products?search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    products = resp.json().get("products", [])
    
    if not products:
        print("No products found.")
        return

    store_ids = set()
    for p in products:
        if p.get("store_id"):
            store_ids.add(p["store_id"])
    
    update_customization(None)
    for s_id in store_ids:
        update_customization(s_id)
    
    for p in products:
        p_id = p['id']
        acc_id = p['konto_allegro_id']
        
        stock = p.get("gapli_product_stock_quantity", 0)
        if stock is None or int(stock) <= 0:
            continue

        permanent_delete(p_id, acc_id)
        time.sleep(3)
        
        send_to_allegro(SKU, acc_id)
        time.sleep(2)

if __name__ == "__main__":
    fix()

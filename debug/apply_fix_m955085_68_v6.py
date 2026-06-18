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
            "249512": "249512_1647420", # Kolor: szary
            "249513": "249513_1647517", # Odcień: grafitowy
            "54": "54_16", # Rozmiar: L/XL
            "225693": "5904726003527", # EAN
            "11323": "11323_1", # Stan: Nowy
            "248811": "248811_958954", # Marka: bez marki
            "15851": "15851_1", # Płeć: kobieta
            "Waga produktu z opakowaniem jednostkowym": "0.3",
            "Nazwa koloru producenta": "Grafitowy",
            "Kod producenta": "157721"
        },
        "is_active": True, "images_mode": "replace"
    }
    resp = requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=payload)
    print(f"Customization update status: {resp.status_code}")
    return resp.status_code in [200, 201]

def permanent_delete(product_id, account_id):
    del_url = "https://gapli.com/api/products-manager/allegro/permanent-delete"
    payload = {"mode": "selected", "product_ids": [{"id": str(product_id), "konto_allegro_id": str(account_id)}]}
    resp = requests.delete(del_url, headers=GAPLI_HEADERS, json=payload)
    return resp.status_code == 200

def send_to_allegro(sku, account_id):
    send_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    send_headers = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}
    payload = {"action": "send", "account_id": str(account_id), "product_skus": [sku], "force_update": True}
    resp = requests.post(send_url, headers=send_headers, json=payload)
    return resp.status_code == 200

def fix():
    url = f"https://gapli.com/api/products-manager/allegro/products?search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    products = resp.json().get("products", [])
    
    store_ids = set()
    for p in products:
        if p.get("store_id"): store_ids.add(p["store_id"])
    
    update_customization(None)
    for s_id in store_ids: update_customization(s_id)
    
    for p in products:
        p_id = p['id']
        acc_id = p['konto_allegro_id']
        if p.get("gapli_product_stock_quantity", 0) > 0:
            print(f"Nuking and re-sending Acc {acc_id}...")
            permanent_delete(p_id, acc_id)
            time.sleep(5)
            send_to_allegro(SKU, acc_id)
            time.sleep(2)

if __name__ == "__main__":
    fix()

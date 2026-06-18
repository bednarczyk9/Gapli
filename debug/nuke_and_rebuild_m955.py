import requests
import json
import time

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_API_KEY = "gapli_ba90f561bf78bf55652e21b5ed33400b7551219e"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "M955085_68"
ACCOUNTS = ["61", "63", "64", "116"]

def nuke_and_rebuild():
    # 1. Delete Existing Customization
    print("Deleting existing customization...")
    # We need to find the ID first
    cust_url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    r_cust = requests.get(cust_url, headers=GAPLI_HEADERS)
    if r_cust.status_code == 200:
        c_id = r_cust.json().get("data", {}).get("id")
        if c_id:
            del_cust_url = f"https://gapli.com/api/product-customizer/customizations/{c_id}"
            r_del_c = requests.delete(del_cust_url, headers=GAPLI_HEADERS)
            print(f"  Customization {c_id} deleted: {r_del_c.status_code}")

    # 2. Permanent Delete integration records for all accounts
    for acc_id in ACCOUNTS:
        print(f"\n--- Cleaning Acc {acc_id} ---")
        search_url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc_id}&search={SKU}"
        resp_p = requests.get(search_url, headers=GAPLI_HEADERS)
        if resp_p.status_code == 200 and resp_p.json().get("products"):
            p_ids = [p["id"] for p in resp_p.json()["products"]]
            print(f"  Found {len(p_ids)} records. Nuking...")
            
            del_url = "https://gapli.com/api/products-manager/allegro/permanent-delete"
            del_payload = {
                "mode": "selected",
                "product_ids": [{"id": str(pid), "konto_allegro_id": str(acc_id)} for pid in p_ids]
            }
            r_del = requests.delete(del_url, headers=GAPLI_HEADERS, json=del_payload)
            print(f"  Delete Result: {r_del.status_code}")
        else:
            print("  No records found.")

    # 3. Create Fresh Customization
    print("\nCreating fresh customization...")
    payload = {
        "sku": SKU,
        "scope": "user",
        "platform": "allegro",
        "custom_name": "Koszula Nocna Ciążowa Model 0192 Grafit - PeeKaBoo",
        "custom_description": "<p>Koszula nocna ciążowa marki PeeKaBoo z napami ułatwiającymi karmienie. Model stworzony z myślą o kobietach w ciąży, idealny do noszenia również po porodzie.  <b>Skład surowcowy:</b>   Wiskoza: 95%  Elastan: 5%   <b>Wymiary dla rozmiaru L/XL:</b>   Długość: 89 cm  Obwód w biodrach: 130 cm  Obwód w biuście: 94 cm</p>",
        "custom_parameters": {
            "Stan": "Nowy",
            "Kolor": "szary",
            "Marka": "bez marki",
            "Rozmiar": "L/XL",
            "EAN (GTIN)": "5904726003527"
        },
        "is_active": True,
        "images_mode": "replace"
    }
    r_save = requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=payload)
    print(f"Customization created: {r_save.status_code}")

    # 4. Trigger Sync
    print("\nTriggering sync...")
    time.sleep(3)
    for acc_id in ACCOUNTS:
        send_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
        send_headers = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}
        send_payload = {
            "action": "send",
            "account_id": acc_id,
            "product_skus": [SKU],
            "force_update": True
        }
        r_send = requests.post(send_url, headers=send_headers, json=send_payload)
        print(f"Acc {acc_id} Send Result: {r_send.text}")

if __name__ == "__main__":
    nuke_and_rebuild()

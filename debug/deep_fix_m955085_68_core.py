import requests
import json
import time

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_API_KEY = "gapli_ba90f561bf78bf55652e21b5ed33400b7551219e"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "M955085_68"

# Param IDs
KOLOR_PARAM_ID = "249512"
SZARY_VALUE_ID = "249512_1647420"
SZARY_LABEL = "szary"

def deep_fix():
    # 1. Fetch all product records for this SKU
    url = f"https://gapli.com/api/products-manager/allegro/products?search={SKU}&mode=full"
    r = requests.get(url, headers=GAPLI_HEADERS)
    if r.status_code != 200:
        print(f"Error fetching products: {r.status_code}")
        return
    
    products = r.json().get('products', [])
    if not products:
        print("No products found.")
        return

    for p in products:
        p_id = p["id"]
        acc_id = p["konto_allegro_id"]
        print(f"\n--- Deep Fixing Product {p_id} (Account {acc_id}) ---")

        # A. Fix Catalog Parameters (The "Core" data)
        cat_params = p.get("allegro_catalog_parameters", [])
        if not cat_params:
            print("  Warning: No catalog parameters found to fix.")
            # If empty, we might need to populate them if they are missing
        else:
            found_kolor = False
            for param in cat_params:
                if param.get("id") == KOLOR_PARAM_ID:
                    print(f"  Updating Kolor param from {param.get('values')} to {SZARY_LABEL}")
                    param["values"] = [SZARY_LABEL]
                    param["valuesIds"] = [SZARY_VALUE_ID]
                    param["_autoResolved"] = False
                    found_kolor = True
            
            if not found_kolor:
                print(f"  Adding missing Kolor param ID {KOLOR_PARAM_ID}")
                cat_params.append({
                    "id": KOLOR_PARAM_ID,
                    "values": [SZARY_LABEL],
                    "valuesIds": [SZARY_VALUE_ID],
                    "_paramScope": "product",
                    "_autoResolved": False
                })

        # B. Reset status and clear error
        payload = {
            "allegro_catalog_parameters": cat_params,
            "allegro_sync_upload_status": "pending",
            "allegro_sync_upload_error_message": None,
            "allegro_sync_upload_retry_count": 0
        }

        # C. Fix "null price" by ensuring settings are present
        if p.get("allegro_sync_upload_error_message") == "Nieprawidłowa cena produktu: null":
            print("  Fixing price error by resetting settings...")
            payload["allegro_offer_settings"] = {
                "price_range": {"min": 50, "max": 50000},
                "pricing_settings": {
                    "markup_increase_value": 0,
                    "markup_increase_percent": 0
                }
            }

        # D. PATCH the product record
        patch_url = f"https://gapli.com/api/products-manager/allegro/products/{p_id}"
        r_patch = requests.patch(patch_url, headers=GAPLI_HEADERS, json=payload)
        if r_patch.status_code == 200:
            print(f"  Successfully patched product record.")
        else:
            print(f"  Failed to patch: {r_patch.status_code} {r_patch.text[:200]}")

    # 2. Trigger Sync for all accounts
    time.sleep(2)
    for acc_id in ["61", "63", "64", "116"]:
        print(f"\nTriggering sync for account {acc_id}...")
        send_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
        send_headers = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}
        send_payload = {
            "action": "send",
            "account_id": acc_id,
            "product_skus": [SKU],
            "force_update": True
        }
        r_send = requests.post(send_url, headers=send_headers, json=send_payload)
        print(f"  Sync result: {r_send.text}")

if __name__ == "__main__":
    deep_fix()

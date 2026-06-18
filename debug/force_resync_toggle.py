import requests
import os
import json
import time

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def force_resync_via_toggle():
    # 1. Fetch current customization
    print(f"Fetching customization for {SKU}...")
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200:
        print(f"Failed to fetch: {resp.status_code}")
        return
    
    data = resp.json().get("data")
    if not data:
        print("No data.")
        return

    # 2. Deactivate
    print("Deactivating...")
    deactivate_payload = {
        "sku": SKU,
        "platform": "allegro",
        "is_active": False
    }
    requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=deactivate_payload)
    time.sleep(2)
    
    # 3. Re-activate with full data
    print("Re-activating...")
    activate_payload = {
        "sku": SKU,
        "scope": "user",
        "platform": "allegro",
        "custom_name": data.get("custom_name"),
        "custom_description": data.get("custom_description"),
        "custom_parameters": data.get("custom_parameters"),
        "is_active": True,
        "images_mode": "replace"
    }
    requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=activate_payload)
    time.sleep(2)
    
    # 4. Trigger Marketplace Send
    print("Triggering Marketplace Send...")
    api_key = os.environ.get("Gapli_Apikey")
    send_headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    send_body = {
        "action": "send",
        "account_id": "116",
        "product_skus": [SKU]
    }
    send_resp = requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=send_headers, json=send_body)
    print(f"Response: {send_resp.text}")

if __name__ == "__main__":
    force_resync_via_toggle()

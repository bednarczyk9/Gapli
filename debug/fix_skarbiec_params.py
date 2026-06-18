import requests
import os
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def fix_and_reset():
    # 1. Fetch current (to keep name and desc)
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    
    data = resp.json().get("data", {})
    
    # 2. Save with EMPTY custom_parameters (forcing null/empty object)
    # This should overwrite any "inconsistent" internal state
    payload = {
        "sku": SKU,
        "scope": "user",
        "platform": "allegro",
        "custom_name": data.get("custom_name"),
        "custom_description": data.get("custom_description"),
        "custom_parameters": {}, # Force empty object instead of null
        "is_active": True,
        "images_mode": "replace"
    }
    
    print("Saving customization with empty parameters object...")
    up_url = "https://gapli.com/api/product-customizer/customizations"
    up_resp = requests.post(up_url, headers=GAPLI_HEADERS, json=payload)
    print(f"Save Result: {up_resp.status_code}")
    
    # 3. Trigger Marketplace Send
    api_key = os.environ.get("Gapli_Apikey")
    send_headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    send_body = {
        "action": "send",
        "account_id": "63",
        "product_skus": [SKU]
    }
    print("Triggering marketplace send for account 63...")
    send_resp = requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=send_headers, json=send_body)
    print(f"Marketplace Result: {send_resp.text}")

if __name__ == "__main__":
    fix_and_reset()

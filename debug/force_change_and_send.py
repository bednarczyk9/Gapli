import requests
import json
import os

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def force_change_and_send():
    # 1. Fetch current
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    
    data = resp.json().get("data", {})
    
    # 2. Update name slightly to force state change
    payload = data
    payload["custom_name"] = data.get("custom_name", "") + " ." # Add a dot
    
    up_url = "https://gapli.com/api/product-customizer/customizations"
    requests.post(up_url, headers=GAPLI_HEADERS, json=payload)
    
    # 3. Trigger Send
    api_key = os.environ.get("Gapli_Apikey")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    r = requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=headers, json={
        "action": "send",
        "account_id": "63",
        "product_skus": [SKU]
    })
    print(f"Force change result: {r.text}")

if __name__ == "__main__":
    force_change_and_send()

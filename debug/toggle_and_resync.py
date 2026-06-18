import requests
import json
import os
import time

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def toggle_and_resync():
    print(f"Toggling customization for {SKU}...")
    
    # 1. Fetch
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    data = resp.json().get("data")
    
    # 2. Deactivate
    payload = data
    payload["is_active"] = False
    requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=payload)
    print("Deactivated.")
    time.sleep(2)
    
    # 3. Reactivate
    payload["is_active"] = True
    requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=payload)
    print("Reactivated.")
    
    # 4. Trigger Send for account 63
    api_key = os.environ.get("Gapli_Apikey")
    requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", 
                  headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, 
                  json={"action": "send", "account_id": "63", "product_skus": [SKU]})
    print("Triggered.")

if __name__ == "__main__":
    toggle_and_resync()

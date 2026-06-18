import requests
import os
import json
import time

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def force_resync_via_recreation():
    # 1. Fetch current customization
    print(f"Fetching customization for {SKU}...")
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200:
        print(f"Failed to fetch customization: {resp.status_code}")
        return
    
    data = resp.json()
    if not data.get("success") or not data.get("data"):
        print("No customization found to recreate.")
        return
    
    cust = data["data"]
    cust_id = cust["id"]
    print(f"Found customization ID: {cust_id}")
    
    # Prepare payload for re-creation
    payload = {
        "sku": SKU,
        "scope": "user",
        "platform": "allegro",
        "custom_name": cust.get("custom_name"),
        "custom_description": cust.get("custom_description"),
        "custom_parameters": cust.get("custom_parameters"),
        "is_active": True,
        "images_mode": cust.get("images_mode", "replace")
    }
    
    # 2. Delete existing customization
    print(f"Deleting customization {cust_id}...")
    del_url = f"https://gapli.com/api/product-customizer/customizations/{cust_id}"
    del_resp = requests.delete(del_url, headers=GAPLI_HEADERS)
    if del_resp.status_code in [200, 204]:
        print("Successfully deleted.")
    else:
        print(f"Failed to delete: {del_resp.status_code} {del_resp.text}")
        return
        
    time.sleep(1)
    
    # 3. Re-create customization
    print("Re-creating customization...")
    create_url = "https://gapli.com/api/product-customizer/customizations"
    create_resp = requests.post(create_url, headers=GAPLI_HEADERS, json=payload)
    if create_resp.status_code in [200, 201]:
        print("Successfully re-created.")
        
        # 4. Trigger marketplace send
        print("Triggering marketplace send...")
        send_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
        # We need the GAPLI_API_KEY for this one
        api_key = os.environ.get("Gapli_Apikey")
        send_headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        send_body = {
            "action": "send",
            "account_id": "116", # AlejaOkazji
            "product_skus": [SKU]
        }
        send_resp = requests.post(send_url, headers=send_headers, json=send_body)
        print(f"Marketplace send response ({send_resp.status_code}): {send_resp.text}")
    else:
        print(f"Failed to re-create: {create_resp.status_code} {create_resp.text}")

if __name__ == "__main__":
    force_resync_via_recreation()

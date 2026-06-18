import requests
import json
import os
import time

# Using the JWT token for Gapli internal API
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

ACCOUNT_ID = "63"
SKU = "1053851_131"

def reset_counters_and_status():
    print(f"Deep resetting SKU {SKU} for account {ACCOUNT_ID}...")
    
    # 1. Get the current product state
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200 or not resp.json().get("products"):
        print("Not found.")
        return
        
    p = resp.json()["products"][0]
    p_id = p["id"]
    
    # 2. PATCH the product record to reset ALL error flags and retry counters
    # This directly edits the record in Gapli database
    update_url = f"https://gapli.com/api/products-manager/allegro/products/{p_id}"
    
    payload = {
        "allegro_sync_upload_status": "pending", # Force back to pending
        "allegro_sync_upload_retry_count": 0,    # Reset counters
        "allegro_sync_upload_error_code": None,
        "allegro_sync_upload_error_message": None,
        "allegro_offer_id": None,                # Ensure it tries a new POST
        "allegro_offer_status": None,
        "allegro_sync_status": "pending"
    }
    
    print("Updating Gapli database record directly...")
    up_resp = requests.patch(update_url, headers=GAPLI_HEADERS, json=payload)
    print(f"PATCH Result ({up_resp.status_code}): {up_resp.text[:200]}")
    
    if up_resp.status_code == 200:
        # 3. Trigger Marketplace Send
        api_key = os.environ.get("Gapli_Apikey")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        send_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
        send_body = {"action": "send", "account_id": ACCOUNT_ID, "product_skus": [SKU]}
        print("Triggering send...")
        s_resp = requests.post(send_url, headers=headers, json=send_body)
        print(f"Final Result: {s_resp.text}")

if __name__ == "__main__":
    reset_counters_and_status()

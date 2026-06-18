import requests
import json
import os
import time

# Using the JWT token for Gapli internal API
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

ACCOUNT_ID = "63"
SKU = "1053851_131"

def try_different_update_methods():
    # 1. Get the current product state
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200 or not resp.json().get("products"):
        return
        
    p = resp.json()["products"][0]
    p_id = p["id"]
    
    # Try different ID types if 'id' fails
    p_global_id = p.get("gapli_product_global_unique_id")
    
    payload = {
        "allegro_sync_upload_status": "pending",
        "allegro_sync_upload_retry_count": 0,
        "allegro_sync_upload_error_code": None,
        "allegro_sync_upload_error_message": None,
        "allegro_sync_status": "pending"
    }
    
    # Possible endpoints for updating a product record
    endpoints = [
        f"https://gapli.com/api/products-manager/allegro/products/update/{p_id}",
        f"https://gapli.com/api/products-manager/allegro/products/edit/{p_id}",
        f"https://gapli.com/api/v1/integrations/allegro/products/{p_id}"
    ]
    
    for url in endpoints:
        print(f"Trying PUT to: {url}")
        r = requests.put(url, headers=GAPLI_HEADERS, json=payload)
        print(f"  Response ({r.status_code}): {r.text[:100]}")
        
    # Final attempt: try a generic API ADD but with the same SKU (might overwrite)
    print("\nTrying to 're-add' the product to force overwrite...")
    add_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    api_key = os.environ.get("Gapli_Apikey")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Use 'send' but with extra flag if discovered
    add_payload = {
        "action": "send",
        "account_id": ACCOUNT_ID,
        "product_skus": [SKU],
        "reset_errors": True,
        "force": True
    }
    r = requests.post(add_url, headers=headers, json=add_payload)
    print(f"Add Result: {r.text}")

if __name__ == "__main__":
    try_different_update_methods()

import requests
import json
import os
import time

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = "63"
SKU = "1053851_131"

def force_refresh_via_api():
    # Attempt to reset the description cache in Gapli by updating the product mapping record.
    # We found the record ID is 2977052.
    # We need to find the working PATCH/PUT endpoint.
    
    # Let's try to fetch by SKU search but with a specific store_id
    search_url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={SKU}"
    resp = requests.get(search_url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    
    p = resp.json().get("products", [])[0]
    p_id = p["id"]
    
    # Try to 're-save' the product settings which might clear the catalog cache
    # Endpoints often used for saving settings in Gapli:
    save_url = f"https://gapli.com/api/products-manager/allegro/products/{p_id}/settings"
    payload = {
        "settings": {
            "price_range": {"min": 50, "max": 20000}
        }
    }
    print(f"Trying to save settings to {save_url}...")
    r = requests.post(save_url, headers=GAPLI_HEADERS, json=payload)
    print(f"  Result: {r.status_code}")
    
    # Try to trigger a 'refresh-catalog' action if such exists
    actions_url = f"https://gapli.com/api/products-manager/allegro/products/{p_id}/actions"
    payload_action = {"action": "refresh_catalog"}
    print(f"Trying action to {actions_url}...")
    ar = requests.post(actions_url, headers=GAPLI_HEADERS, json=payload_action)
    print(f"  Result: {ar.status_code}")

if __name__ == "__main__":
    force_refresh_via_api()

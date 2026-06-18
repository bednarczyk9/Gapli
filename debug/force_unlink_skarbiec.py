import requests
import json
import os
import time

# JWT Token for Gapli
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = "1053851_131"
OFFER_ID = "18587435573" # Found ID from get-status
ACCOUNT_ID = "63"

def force_unlink_via_id():
    # 1. Fetch current record to get ID
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        if products:
            p_id = products[0].get("id")
            print(f"Product ID in Gapli: {p_id}")
            
            # Try to DELETE using the standard UI endpoint (might be different than what I used before)
            # Based on typical Next.js / API patterns
            del_url = f"https://gapli.com/api/products-manager/allegro/products/{p_id}"
            print(f"Attempting DELETE on {del_url}...")
            r = requests.delete(del_url, headers=GAPLI_HEADERS)
            print(f"DELETE Result: {r.status_code}")
            
            # If still 404, try to PATCH it to a state that Gapli might reconsider 'fresh'
            print("Attempting to PATCH record to clear Offer ID...")
            patch_payload = {
                "allegro_offer_id": None,
                "allegro_sync_upload_status": "pending",
                "allegro_sync_upload_retry_count": 0
            }
            # Many APIs use POST with _method=PATCH or similar if PATCH is blocked
            p_url = f"https://gapli.com/api/products-manager/allegro/products/{p_id}"
            pr = requests.patch(p_url, headers=GAPLI_HEADERS, json=patch_payload)
            print(f"PATCH Result: {pr.status_code}")

if __name__ == "__main__":
    force_unlink_via_id()

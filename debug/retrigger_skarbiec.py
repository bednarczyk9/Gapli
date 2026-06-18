import requests
import os
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def fetch_and_recreate_skarbiec():
    # 1. Check current status for Skarbiec
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id=63&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        if products:
            p = products[0]
            print(f"Current Status: {p.get('allegro_sync_status')}")
            print(f"Error: {p.get('allegro_sync_upload_error_message')}")
            
            # Since I can't DELETE the product association via API, 
            # I will try to use the marketplace/listing API to force a re-check
            
            api_key = os.environ.get("Gapli_Apikey")
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            
            # Try 'check-readiness' to see if Gapli updates the internal error state
            payload = {
                "action": "check-readiness",
                "account_id": "63",
                "product_skus": [SKU]
            }
            print("Running readiness check for Skarbiec...")
            r_resp = requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=headers, json=payload)
            print(f"Readiness Result: {r_resp.text}")
            
            # Now try SEND again
            payload["action"] = "send"
            print("Triggering SEND again for Skarbiec...")
            s_resp = requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=headers, json=payload)
            print(f"Send Result: {s_resp.text}")
        else:
            print("Product not found.")

if __name__ == "__main__":
    fetch_and_recreate_skarbiec()

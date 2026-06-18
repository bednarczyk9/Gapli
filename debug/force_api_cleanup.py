import requests
import os
import json
import time

# Using the JWT token for Gapli internal API
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

# Using the API Key for listing actions
GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
LISTING_HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}

ACCOUNT_ID = "63" # skarbiec_ofert
SKU = "1053851_131"

def force_api_cleanup():
    # 1. Fetch the exact product ID for THIS specific account mapping
    print(f"Finding product record for SKU {SKU} on account {ACCOUNT_ID}...")
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    
    if resp.status_code != 200:
        print(f"Fetch failed: {resp.status_code}")
        return

    products = resp.json().get("products", [])
    if not products:
        print("Product not found in Gapli for this account.")
        return

    p_data = products[0]
    p_id = p_data.get("id")
    print(f"Found product ID: {p_id}")

    # 2. Attempt hard delete of the association
    # We try the standard DELETE endpoint for allegro products
    print(f"Attempting to DELETE record {p_id} from Gapli...")
    del_url = f"https://gapli.com/api/products-manager/allegro/products/{p_id}"
    del_resp = requests.delete(del_url, headers=GAPLI_HEADERS)
    
    # Sometimes Gapli needs a body even for DELETE, or uses a different verb
    print(f"Delete Response ({del_resp.status_code}): {del_resp.text[:200]}")
    
    if del_resp.status_code not in [200, 204]:
        print("Standard DELETE failed. Trying bulk remove action...")
        bulk_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
        bulk_payload = {
            "action": "remove", # Some internal APIs use 'remove' to unlink
            "account_id": ACCOUNT_ID,
            "product_skus": [SKU]
        }
        bulk_resp = requests.post(bulk_url, headers=LISTING_HEADERS, json=bulk_payload)
        print(f"Bulk Remove Response: {bulk_resp.text}")

    # 3. Wait and trigger fresh send
    time.sleep(2)
    print("Triggering fresh SEND...")
    send_payload = {
        "action": "send",
        "account_id": ACCOUNT_ID,
        "product_skus": [SKU]
    }
    send_resp = requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=LISTING_HEADERS, json=send_payload)
    print(f"Final Send Result: {send_resp.text}")

if __name__ == "__main__":
    force_api_cleanup()

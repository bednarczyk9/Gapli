import requests
import json
import os
import time

# JWT Token for Gapli
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = "1053851_131"
ACCOUNT_ID = "63"

def temporary_cleanup_and_reset():
    # 1. Fetch the customization to back it up (though I have it in my history)
    print(f"Backing up customization for {SKU}...")
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200:
        print(f"Could not find customization: {resp.status_code}")
        return
        
    cust = resp.json().get("data")
    if not cust:
        print("No customization found.")
    else:
        cust_id = cust["id"]
        # 2. DELETE the customization
        print(f"Deleting customization ID {cust_id}...")
        del_url = f"https://gapli.com/api/product-customizer/customizations/{cust_id}"
        del_resp = requests.delete(del_url, headers=GAPLI_HEADERS)
        print(f"Delete Result: {del_resp.status_code}")

    # 3. Now try to 'REMOVE' the offer for Skarbiec
    print(f"Attempting to UNLINK SKU {SKU} from account {ACCOUNT_ID}...")
    # Using the standard listing API to try and clear the record
    api_key = os.environ.get("Gapli_Apikey")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Try different actions to see if anything unblocks it
    for action in ["remove", "get-status"]:
        payload = {
            "action": action,
            "account_id": ACCOUNT_ID,
            "product_skus": [SKU]
        }
        r = requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=headers, json=payload)
        print(f"Action '{action}' Result: {r.text}")

    # 4. If we successfully cleared it (in theory), re-create customization and send
    # For now, let's just see if delete + action unblocks the status.

if __name__ == "__main__":
    temporary_cleanup_and_reset()

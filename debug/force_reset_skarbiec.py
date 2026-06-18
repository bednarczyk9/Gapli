import requests
import os
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = "63" # skarbiec_ofert
SKU = "1053851_131"

def force_delete_allegro_data():
    # 1. Fetch the product internal ID for this account
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        if products:
            p_id = products[0].get("id")
            print(f"Internal Product ID: {p_id}")
            
            # 2. Try to perform a manual reset by sending a null state
            # This is a bit of a hack but might clear the max_retries/405 state
            reset_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
            api_key = os.environ.get("Gapli_Apikey")
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            
            # 'remove' might clear the association without deleting the actual offer if ID is null
            payload = {
                "action": "remove",
                "account_id": ACCOUNT_ID,
                "product_skus": [SKU]
            }
            print(f"Attempting 'remove' action to reset state...")
            r_resp = requests.post(reset_url, headers=headers, json=payload)
            print(f"Remove Result: {r_resp.text}")
            
            # Now try to re-add
            payload["action"] = "send"
            print(f"Attempting fresh 'send' action...")
            s_resp = requests.post(reset_url, headers=headers, json=payload)
            print(f"Send Result: {s_resp.text}")
        else:
            print("Product not found.")

if __name__ == "__main__":
    force_delete_allegro_data()

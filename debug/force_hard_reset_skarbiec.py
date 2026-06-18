import requests
import os
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = "63" # skarbiec_ofert
SKU = "1053851_131"

def force_delete_product():
    # 1. Fetch internal ID
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        if products:
            p_id = products[0].get("id")
            print(f"Product ID in Gapli: {p_id}")
            
            # 2. DELETE product association for THIS account
            # This should allow Gapli to 'forget' it was ever there and failed
            del_url = f"https://gapli.com/api/products-manager/allegro/products/{p_id}"
            print(f"Deleting product association {p_id}...")
            d_resp = requests.delete(del_url, headers=GAPLI_HEADERS)
            print(f"Delete Result ({d_resp.status_code}): {d_resp.text}")
            
            if d_resp.status_code in [200, 204]:
                # 3. Trigger fresh SEND
                print("Re-sending SKU to marketplace...")
                send_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
                api_key = os.environ.get("Gapli_Apikey")
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "action": "send",
                    "account_id": ACCOUNT_ID,
                    "product_skus": [SKU]
                }
                s_resp = requests.post(send_url, headers=headers, json=payload)
                print(f"Send Result: {s_resp.text}")
        else:
            print("Product not found.")

if __name__ == "__main__":
    force_delete_product()

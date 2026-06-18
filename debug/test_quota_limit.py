import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"}

def try_add_new_sku():
    # Account 116 (AlejaOkazji)
    # Pick a random SKU from wholesalers or another account
    sku = "ND28_13110_PA_JT5007_ZIE_30" # Just a sample SKU
    
    body = {
        "action": "send",
        "account_id": "116",
        "product_skus": [sku]
    }
    
    print(f"Attempting to add new SKU {sku} to account 116...")
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    resp = requests.post(url, headers=HEADERS, json=body)
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.text}")

if __name__ == "__main__":
    try_add_new_sku()

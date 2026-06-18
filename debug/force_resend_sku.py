import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
GAPLI_HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}
ACCOUNT_ID = "116" # AlejaOkazji
SKU = "1053851_131"

def force_resend():
    print(f"Force resending SKU {SKU} to marketplace...")
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    body = {
        "action": "send",
        "account_id": ACCOUNT_ID,
        "product_skus": [SKU],
        "force_update": True # Try to add this if it exists
    }
    
    resp = requests.post(url, headers=GAPLI_HEADERS, json=body)
    print(f"Response ({resp.status_code}):")
    print(resp.text)

if __name__ == "__main__":
    force_resend()

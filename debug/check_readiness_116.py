import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def list_actions():
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    
    # We found 'send', 'check-readiness', 'get-status'
    # Let's try to check readiness for account 116
    
    body = {
        "action": "check-readiness",
        "account_id": "116",
        "product_skus": ["ND09_KX3052_30"] # Sample SKU
    }
    
    print(f"Checking readiness for account 116...")
    resp = requests.post(url, headers=HEADERS, json=body)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    list_actions()

import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"}

def try_full_readiness():
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    
    body = {
        "action": "check-readiness",
        "account_id": "116"
    }
    
    print(f"POST {url} with action: check-readiness (account level)")
    resp = requests.post(url, headers=HEADERS, json=body)
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.text}")

if __name__ == "__main__":
    try_full_readiness()

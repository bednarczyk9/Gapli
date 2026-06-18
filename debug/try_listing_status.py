import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"}

def try_get_status():
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    
    body = {
        "action": "get-status",
        "account_id": "116"
    }
    
    print(f"POST {url} with action: get-status")
    resp = requests.post(url, headers=HEADERS, json=body)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"  Response: {resp.text}")

if __name__ == "__main__":
    try_get_status()

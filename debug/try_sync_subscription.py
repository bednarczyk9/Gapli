import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"}

def try_sync_sub():
    url = "https://gapli.com/api/v1/integrations/marketplace/accounts"
    
    body = {
        "action": "sync-subscription",
        "account_id": "116"
    }
    
    print(f"POST {url} with action: sync-subscription")
    resp = requests.post(url, headers=HEADERS, json=body)
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.text}")

if __name__ == "__main__":
    try_sub_settings = [
        "https://gapli.com/api/v1/integrations/marketplace/accounts/sync-subscription",
        "https://gapli.com/api/v1/integrations/marketplace/accounts/116/sync-subscription",
    ]
    
    try_sync_sub()
    
    for u in try_sub_settings:
        print(f"POST {u}")
        resp = requests.post(u, headers=HEADERS)
        print(f"  Status: {resp.status_code}")

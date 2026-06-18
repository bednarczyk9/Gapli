import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def sync_account():
    # Attempt common sync/refresh actions
    # We'll try POST to an action endpoint on the account
    account_id = 116
    urls = [
        f"https://gapli.com/api/v1/integrations/marketplace/accounts/{account_id}/sync",
        f"https://gapli.com/api/v1/integrations/marketplace/accounts/{account_id}/refresh",
        f"https://gapli.com/api/v1/integrations/marketplace/accounts/{account_id}/reconnect",
    ]
    
    for url in urls:
        print(f"POST {url}")
        resp = requests.post(url, headers=HEADERS)
        print(f"  Status: {resp.status_code}")
        if resp.status_code in [200, 201, 202, 204]:
             print(f"  Success: {resp.text}")
        else:
             print(f"  Error: {resp.text[:200]}")

if __name__ == "__main__":
    sync_account()

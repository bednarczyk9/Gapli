import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"}

def try_sync_limit():
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    
    actions = ["sync", "refresh", "update-limit", "sync-limits", "reconnect"]
    
    for action in actions:
        print(f"Trying action: {action}...")
        body = {
            "action": action,
            "account_id": "116"
        }
        resp = requests.post(url, headers=HEADERS, json=body)
        print(f"  Status: {resp.status_code}")
        print(f"  Response: {resp.text}")

if __name__ == "__main__":
    try_sync_limit()

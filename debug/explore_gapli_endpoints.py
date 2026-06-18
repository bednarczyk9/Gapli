import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def list_all_integrations_endpoints():
    endpoints = [
        "https://gapli.com/api/v1/integrations/marketplace/accounts",
        "https://gapli.com/api/v1/integrations/marketplace/settings",
        "https://gapli.com/api/v1/integrations/marketplace/status",
        "https://gapli.com/api/v1/integrations/marketplace/sync",
    ]
    
    for url in endpoints:
        print(f"GET {url}")
        resp = requests.get(url, headers=HEADERS)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Response: {json.dumps(resp.json(), indent=2)[:500]}...")
        else:
            print(f"  Error: {resp.text[:200]}")

if __name__ == "__main__":
    list_all_integrations_endpoints()

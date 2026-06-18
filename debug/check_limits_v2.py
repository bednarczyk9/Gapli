import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def list_more():
    urls = [
        "https://gapli.com/api/v1/integrations/marketplace/limits",
        "https://gapli.com/api/v1/integrations/marketplace/quotas",
        "https://gapli.com/api/v1/user/limits",
        "https://gapli.com/api/v1/account/limits",
        "https://gapli.com/api/v1/integrations/marketplace/accounts/116/settings",
    ]
    for url in urls:
        print(f"GET {url}")
        resp = requests.get(url, headers=HEADERS)
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Response: {json.dumps(resp.json(), indent=2)}")

if __name__ == "__main__":
    list_more()

import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def check_options():
    # Try different variations of the account endpoint
    urls = [
        "https://gapli.com/api/v1/integrations/marketplace/accounts/116",
        "https://gapli.com/api/v1/integrations/marketplace/accounts",
        "https://gapli.com/api/v1/integrations/stores/308",
    ]
    
    for url in urls:
        print(f"OPTIONS {url}")
        resp = requests.options(url, headers=HEADERS)
        print(f"  Status: {resp.status_code}")
        print(f"  Allow: {resp.headers.get('Allow')}")
        print(f"  Access-Control-Allow-Methods: {resp.headers.get('Access-Control-Allow-Methods')}")

if __name__ == "__main__":
    check_options()

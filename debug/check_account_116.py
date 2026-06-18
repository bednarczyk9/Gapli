import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def get_account_id_116():
    url = "https://gapli.com/api/v1/integrations/marketplace/accounts/116"
    resp = requests.get(url, headers=HEADERS)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print(json.dumps(resp.json(), indent=4))
    else:
        print(resp.text)

if __name__ == "__main__":
    get_account_id_116()

import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def get_gapli_accounts():
    url = "https://gapli.com/api/v1/integrations/marketplace/accounts"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        accounts = resp.json().get("accounts", [])
        for acc in accounts:
            print(f"Account: {acc.get('store_name')} (ID: {acc.get('id')})")
            print(f"  Platform: {acc.get('platform')}")
            print(f"  Allegro Login: {acc.get('allegro_login')}")
            # print(f"  Data: {json.dumps(acc, indent=2)}")
    else:
        print(f"Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    get_gapli_accounts()

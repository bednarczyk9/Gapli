import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def get_account_details():
    account_id = 116
    print(f"Fetching details for account {account_id}...")
    
    url = "https://gapli.com/api/v1/integrations/marketplace/accounts"
    resp = requests.get(url, headers=HEADERS)
    
    if resp.status_code == 200:
        accounts = resp.json().get("accounts", [])
        aleja = next((acc for acc in accounts if str(acc.get('id')) == str(account_id)), None)
        if aleja:
            print(json.dumps(aleja, indent=4))
        else:
            print("Account 116 not found in the list.")
    else:
        print(f"Error: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    get_account_details()

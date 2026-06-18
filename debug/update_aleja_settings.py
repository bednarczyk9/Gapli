import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def update_account_116():
    # Attempting to re-save account details with the store_id
    # We found store_id: 308 for AlejaOkazji
    url = "https://gapli.com/api/v1/integrations/marketplace/accounts"
    
    # Let's try to find if there is a PUT/PATCH endpoint for account update
    # We don't have it, but we can try POSTing the same data to see if it refreshes
    
    body = {
        "id": "116",
        "name": "AlejaOkazji",
        "store_id": "308"
    }
    
    print(f"Attempting to UPDATE/REFRESH account 116 settings...")
    # This is speculative.
    resp = requests.post(url, headers=HEADERS, json=body)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    update_account_116()

import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def check_statuses():
    account_id = 61
    print(f"Checking product statuses for account {account_id}...")
    
    # Fetch a sample to see available statuses
    url = f"https://gapli.com/api/v1/integrations/marketplace/products?account_id={account_id}&limit=1"
    resp = requests.get(url, headers=HEADERS)
    
    if resp.status_code == 200:
        data = resp.json()
        total = data.get("pagination", {}).get("total", 0)
        print(f"Total products in Gapli for this account: {total}")
        
        # Now let's try to find how many are NOT active
        # Gapli might support filtering by status
        for status in ["active", "draft", "ended", "error", "pending"]:
            url_stat = f"https://gapli.com/api/v1/integrations/marketplace/products?account_id={account_id}&status={status}&limit=1"
            resp_stat = requests.get(url_stat, headers=HEADERS)
            if resp_stat.status_code == 200:
                s_total = resp_stat.json().get("pagination", {}).get("total", 0)
                print(f" - {status}: {s_total}")
            else:
                print(f" - {status}: (failed to fetch)")
    else:
        print(f"Failed to fetch products: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    check_statuses()

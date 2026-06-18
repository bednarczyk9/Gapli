import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def dump_accounts():
    url = "https://gapli.com/api/v1/integrations/marketplace/accounts"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        with open("full_accounts_dump.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Dumped accounts to full_accounts_dump.json")
        
        for acc in data.get("accounts", []):
            print(f"Account: {acc.get('name')} (ID: {acc.get('id')})")
            for k, v in acc.items():
                if "limit" in k.lower() or "quota" in k.lower() or "count" in k.lower() or "max" in k.lower():
                    print(f"  {k}: {v}")
    else:
        print(f"Error: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    dump_accounts()

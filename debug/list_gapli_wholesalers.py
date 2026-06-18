import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def list_wholesalers():
    url = "https://gapli.com/api/v1/integrations/wholesalers"
    resp = requests.get(url, headers=HEADERS)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Wholesalers: {len(data.get('wholesalers', []))}")
        for w in data.get('wholesalers', [])[:10]:
            print(f" - {w.get('name')} (ID: {w.get('id')})")
    else:
        print(resp.text)

if __name__ == "__main__":
    list_wholesalers()

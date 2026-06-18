import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def check_settings():
    url = "https://gapli.com/api/v1/settings"
    resp = requests.get(url, headers=HEADERS)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print(json.dumps(resp.json(), indent=2))
    else:
        # Try /api/v1/user/settings
        url_u = "https://gapli.com/api/v1/user/settings"
        resp_u = requests.get(url_u, headers=HEADERS)
        print(f"User Settings Status: {resp_u.status_code}")
        if resp_u.status_code == 200:
             print(json.dumps(resp_u.json(), indent=2))

if __name__ == "__main__":
    check_settings()

import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def check_plan():
    url = "https://gapli.com/api/v1/user/plan"
    resp = requests.get(url, headers=HEADERS)
    print(f"Plan Status: {resp.status_code}")
    if resp.status_code == 200:
        print(json.dumps(resp.json(), indent=4))
    else:
        # Try /api/v1/profile
        url_p = "https://gapli.com/api/v1/profile"
        resp_p = requests.get(url_p, headers=HEADERS)
        print(f"Profile Status: {resp_p.status_code}")
        if resp_p.status_code == 200:
             print(json.dumps(resp_p.json(), indent=4))

if __name__ == "__main__":
    check_plan()

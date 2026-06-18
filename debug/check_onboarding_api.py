import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def check_onboarding():
    url = "https://gapli.com/api/v1/dashboard-home/onboarding-status"
    resp = requests.get(url, headers=HEADERS)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print(json.dumps(resp.json(), indent=2))
    else:
        # Try without /v1/
        url_internal = "https://gapli.com/api/dashboard-home/onboarding-status"
        resp_i = requests.get(url_internal, headers=HEADERS)
        print(f"Internal Status: {resp_i.status_code}")
        if resp_i.status_code == 200:
             print(json.dumps(resp_i.json(), indent=2))

if __name__ == "__main__":
    check_onboarding()

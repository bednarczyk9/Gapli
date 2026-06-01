import requests
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def check_account_limits():
    urls = [
        "https://gapli.com/api/dashboard-home/onboarding-status",
        "https://gapli.com/api/auth/me",
        "https://gapli.com/api/store-manager/stores?limit=10"
    ]
    for url in urls:
        print(f"Checking {url}...")
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    check_account_limits()

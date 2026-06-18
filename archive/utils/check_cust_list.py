import requests
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def check_list():
    url = "https://gapli.com/api/product-customizer/customizations-list?limit=5"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    else:
        print(f"Error: {resp.status_code}")

if __name__ == "__main__":
    check_list()

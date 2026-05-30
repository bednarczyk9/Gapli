import requests
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def fetch_sample_customization():
    url = "https://gapli.com/api/product-customizer/customizations-list?limit=1"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", [])
        if items:
            print(json.dumps(items[0], indent=4, ensure_ascii=False))
        else:
            print("No customizations found.")
    else:
        print(f"Error: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    fetch_sample_customization()

import requests
import json
import sys

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

def check(sku):
    url = f"https://gapli.com/api/product-customizer/customizations?sku={sku}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        data = resp.json().get("data")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    sku = sys.argv[1] if len(sys.argv) > 1 else "11998_88"
    check(sku)

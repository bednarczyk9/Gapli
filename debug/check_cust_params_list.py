import json

# Let's see how parameters look in a previously pulled file if any
import requests

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

def check():
    url = f"https://gapli.com/api/product-customizer/customizations-list?limit=5"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    for p in resp.json().get('items', []):
        print("SKU:", p['sku'])
        print(type(p.get('custom_parameters')))
        print(p.get('custom_parameters'))

if __name__ == "__main__":
    check()

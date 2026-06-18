import requests
import json
import os

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def find_all_custs():
    # Try searching by SKU in the list
    url = f"https://gapli.com/api/product-customizer/customizations-list?sku={SKU}"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        items = resp.json().get("items", [])
        print(f"Found {len(items)} customizations for SKU {SKU}")
        for i in items:
            print(f"ID: {i.get('id')}, Store: {i.get('store_id')}, Platform: {i.get('platform')}")
            desc = i.get('custom_description', '')
            print(f"Broken tags present: {'.<b></p>' in desc or ').<b></p>' in desc}")
    else:
        print(f"Error: {resp.status_code}")

if __name__ == "__main__":
    find_all_custs()

import requests
import os
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"
ACCOUNT_ID = "116"

def try_sync_endpoints():
    endpoints = [
        "https://gapli.com/api/products-manager/allegro/products/sync",
        "https://gapli.com/api/products-manager/allegro/products/sync-to-allegro"
    ]
    
    for url in endpoints:
        print(f"Trying endpoint: {url}")
        # Try both body types
        payloads = [
            {"skus": [SKU]},
            {"sku": SKU, "konto_allegro_id": ACCOUNT_ID}
        ]
        
        for payload in payloads:
            print(f"  Payload: {payload}")
            try:
                resp = requests.post(url, headers=GAPLI_HEADERS, json=payload)
                print(f"  Response ({resp.status_code}): {resp.text[:200]}")
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    try_sync_endpoints()

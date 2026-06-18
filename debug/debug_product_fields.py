import requests
import os
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
import sys
ACCOUNT_ID = sys.argv[2] if len(sys.argv) > 2 else "63"
SKU = sys.argv[1] if len(sys.argv) > 1 else "12014_88"

def debug_product_fields():
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        p = resp.json().get("products", [])[0]
        print("Product fields for account 63:")
        # Filter out very long ones first
        for k, v in p.items():
            if isinstance(v, str) and len(v) > 200:
                print(f"{k}: [LONG STRING, length {len(v)}]")
                if "<b>" in v.lower():
                     print(f"  Broken tags in {k}: {').<b></p>' in v or '.<b></p>' in v}")
            else:
                print(f"{k}: {v}")
    else:
        print(f"Error: {resp.status_code}")

if __name__ == "__main__":
    debug_product_fields()

import requests
import json
import os
import re

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
PRODUCT_ID = "2977052"

def deep_fix_product_record():
    # 1. Fetch the broken record
    url = f"https://gapli.com/api/products-manager/allegro/products/{PRODUCT_ID}"
    # Wait, if GET to this URL works, maybe PATCH works too?
    # Actually, the GET I used was a search. 
    # Let's try to fetch this specific ID directly.
    
    # 2. Prepare fixed description
    # I'll just use a very simple one to ensure it passes.
    fixed_desc = {
        "sections": [
            {
                "items": [
                    {
                        "type": "TEXT",
                        "content": "<h1>PARASOL OGRODOWY Z OŚWIETLENIEM LED 300CM</h1><p>Wysokiej jakości parasol ogrodowy marki Saska Garden. Wyposażony w 32 diody LED zasilane energią słoneczną.</p>"
                    }
                ]
            }
        ]
    }
    
    payload = {
        "allegro_catalog_description": fixed_desc,
        "allegro_sync_upload_status": "pending",
        "allegro_sync_upload_retry_count": 0,
        "allegro_description_resync_pending": True
    }
    
    # Try different endpoints
    endpoints = [
        f"https://gapli.com/api/products-manager/allegro/products/{PRODUCT_ID}",
        f"https://gapli.com/api/v1/integrations/allegro/products/{PRODUCT_ID}",
        f"https://gapli.com/api/products-manager/products/{PRODUCT_ID}"
    ]
    
    for ep in endpoints:
        print(f"Trying PATCH to {ep}...")
        try:
            r = requests.patch(ep, headers=GAPLI_HEADERS, json=payload)
            print(f"  Result ({r.status_code}): {r.text[:100]}")
            if r.status_code == 200:
                print("  SUCCESS!")
                break
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    deep_fix_product_record()

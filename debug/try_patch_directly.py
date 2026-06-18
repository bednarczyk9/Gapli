import requests
import json
import os

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
PRODUCT_ID = "2977052"

def try_patch_directly():
    url = f"https://gapli.com/api/v1/integrations/allegro/products/{PRODUCT_ID}"
    
    # Simple, valid description
    desc = {
        "sections": [
            {
                "items": [
                    {
                        "type": "TEXT",
                        "content": "<h1>PARASOL OGRODOWY LED 300CM</h1><p>Wysokiej jakości parasol ogrodowy marki Saska Garden. Wyposażony w 32 diody LED zasilane energią słoneczną.</p>"
                    }
                ]
            }
        ]
    }
    
    payload = {
        "allegro_catalog_description": desc,
        "allegro_sync_upload_status": "pending",
        "allegro_sync_upload_retry_count": 0,
        "allegro_sync_upload_error_message": None
    }
    
    print(f"Trying direct PATCH to {url}...")
    r = requests.patch(url, headers=GAPLI_HEADERS, json=payload)
    print(f"  Result ({r.status_code}): {r.text[:200]}")

if __name__ == "__main__":
    try_patch_directly()

import requests
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
SKU = "M955085_68"

def check():
    url = f'https://gapli.com/api/products-manager/allegro/products?search={SKU}&mode=full'
    resp = requests.get(url, headers={'Authorization': GAPLI_TOKEN})
    data = resp.json()
    for p in data.get("products", []):
        acc = p.get("konto_allegro_id")
        status = p.get("allegro_sync_upload_status")
        err = p.get("allegro_sync_upload_error_message")
        print(f"Acc {acc}: {status} - {err}")

if __name__ == "__main__":
    check()

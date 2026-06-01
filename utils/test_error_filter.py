import requests
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def test_error_filter():
    url = "https://gapli.com/api/products-manager/allegro/products?konto_allegro_id=61&allegro_sync_upload_status=error&limit=10"
    resp = requests.get(url, headers=HEADERS)
    print(f"Testing {url}: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Found {data.get('total', 0)} total errors with this filter.")
        for p in data.get("products", []):
            print(f" - {p.get('sku')}: {p.get('allegro_sync_upload_status')}")

if __name__ == "__main__":
    test_error_filter()

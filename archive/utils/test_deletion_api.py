import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def test_deletion_methods():
    sku = "1004260-660_150"
    
    # Get IDs first
    url = f"https://gapli.com/api/product-customizer/customizations-list?sku={sku}"
    resp = requests.get(url, headers=HEADERS)
    items = resp.json().get("items", [])
    if not items:
        print("No items found to delete.")
        return
    
    cid = items[0].get("id")
    print(f"Testing deletion for ID: {cid}, SKU: {sku}")
    
    # Try different endpoints
    tests = [
        f"https://gapli.com/api/product-customizer/customizations/{cid}",
        f"https://gapli.com/api/product-customizer/customizations?id={cid}",
        f"https://gapli.com/api/product-customizer/items/{cid}",
        f"https://gapli.com/api/product-customizer/customizations/delete?sku={sku}",
        f"https://gapli.com/api/product-customizer/customizations?sku={sku}"
    ]
    
    for t_url in tests:
        print(f"Testing DELETE on {t_url}...")
        try:
            r = requests.delete(t_url, headers=HEADERS)
            print(f"  Status: {r.status_code}")
            if r.status_code in [200, 204]:
                print(f"  SUCCESS on {t_url}")
                return
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_deletion_methods()

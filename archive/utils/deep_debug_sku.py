import requests
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def deep_debug_sku():
    sku = "3343-ZW_307"
    
    # 1. Fetch from customizations-list (shows everything)
    url = f"https://gapli.com/api/product-customizer/customizations-list?sku={sku}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        items = resp.json().get("items", [])
        print(f"Found {len(items)} customization entries for {sku}")
        for item in items:
            print(f"--- Entry ID: {item.get('id')}, Platform: {item.get('platform')}, Scope: {item.get('scope')} ---")
            print(f"Parameters: {json.dumps(item.get('custom_parameters'), indent=2, ensure_ascii=False)}")
    
    # 2. Check the product details in products-manager
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id=61&search={sku}&mode=full"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        p = resp.json()["products"][0]
        print(f"\n--- Product Manager Status for {sku} ---")
        print(f"Sync Status: {p.get('allegro_sync_upload_status')}")
        print(f"Error Message: {p.get('allegro_sync_upload_error_message')}")
        print(f"Category ID: {p.get('allegro_offer_category_id')}")

if __name__ == "__main__":
    deep_debug_sku()

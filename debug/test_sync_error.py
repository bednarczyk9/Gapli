import requests
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "12014_88"

def trigger_sync_and_wait():
    url = "https://gapli.com/api/products-manager/allegro/products/sync?konto_allegro_id=63"
    resp = requests.post(url, headers=GAPLI_HEADERS, json={"skus": [SKU]})
    print(f"Sync trigger response: {resp.status_code}")
    
    import time
    for i in range(10):
        print(f"Waiting for result... ({i+1}/10)")
        time.sleep(3)
        check_url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id=63&search={SKU}&mode=full"
        r = requests.get(check_url, headers=GAPLI_HEADERS).json()
        p = r['products'][0]
        if p.get('allegro_sync_upload_error_message'):
            print(f"Error: {p['allegro_sync_upload_error_message']}")
            print(f"API Response: {p.get('allegro_api_response')}")
            # If we have API response, break
            if p.get('allegro_api_response'):
                break
        else:
            print(f"Status: {p.get('allegro_offer_status')}")

if __name__ == "__main__":
    trigger_sync_and_wait()

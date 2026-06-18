import requests
import json
import sys

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = sys.argv[1] if len(sys.argv) > 1 else "12014_88"

for acc in [116, 61, 64, 63]:
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc}&search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS).json()
    for p in resp.get("products", []):
        if p["sku"] == SKU:
            print(f"--- Account {acc} ---")
            print(f"Status: {p.get('allegro_offer_status')}")
            print(f"Sync Message: {p.get('allegro_sync_upload_error_message')}")
            
            api_resp = p.get("allegro_api_response")
            if api_resp:
                print("API Response:")
                if isinstance(api_resp, str):
                    try:
                        print(json.dumps(json.loads(api_resp), indent=2, ensure_ascii=False))
                    except:
                        print(api_resp)
                else:
                    print(json.dumps(api_resp, indent=2, ensure_ascii=False))
            print()

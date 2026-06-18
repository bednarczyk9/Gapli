import requests
import time
import json
import os

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
GAPLI_API_KEY = "gapli_ba90f561bf78bf55652e21b5ed33400b7551219e"
SKU = "M955085_68"

def fix():
    url = f"https://gapli.com/api/products-manager/allegro/products?search={SKU}&mode=full"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    products = resp.json().get("products", [])
    
    for p in products:
        p_id = p['id']
        acc_id = p['konto_allegro_id']
        
        # 1. Try to 'unlink' via action
        print(f"Trying to unlink ID {p_id} (Acc {acc_id})...")
        act_url = f"https://gapli.com/api/products-manager/allegro/products/{p_id}/actions"
        resp_act = requests.post(act_url, headers=GAPLI_HEADERS, json={"action": "unlink"})
        print(f"  Unlink status: {resp_act.status_code}")
        
        # 2. Try to 'refresh_catalog'
        print(f"Trying to refresh_catalog ID {p_id}...")
        resp_ref = requests.post(act_url, headers=GAPLI_HEADERS, json={"action": "refresh_catalog"})
        print(f"  Refresh status: {resp_ref.status_code}")
        
        # 3. Re-send
        time.sleep(2)
        send_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
        send_headers = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}
        payload = {"action": "send", "account_id": str(acc_id), "product_skus": [SKU], "force_update": True}
        requests.post(send_url, headers=send_headers, json=payload)

if __name__ == "__main__":
    fix()

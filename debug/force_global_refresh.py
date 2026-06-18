import requests
import json
import os

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def force_global_refresh():
    # 1. Update the GLOBAL CUSTOMIZATION for ID 25 one more time
    # This time, I will add a tiny SALES TEXT at the end to be 100% sure it's new.
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    
    data = resp.json().get("data", {})
    fixed_html = data.get("custom_description", "")
    
    # Ensure it's clean and has a unique marker
    fixed_html = fixed_html.replace('</b></b>', '</b>').replace('<b><b>', '<b>')
    fixed_html += "<p><b>OFERTA OGRANICZONA CZASOWO!</b></p>"
    
    payload = data
    payload["custom_description"] = fixed_html
    payload["custom_name"] = "PARASOL OGRODOWY LED 300CM COCCORA - SASKA GARDEN"
    
    up_url = "https://gapli.com/api/product-customizer/customizations"
    requests.post(up_url, headers=GAPLI_HEADERS, json=payload)
    print("Updated global customization with marker.")
    
    # 2. Trigger SEND for account 63
    api_key = os.environ.get("Gapli_Apikey")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    send_payload = {
        "action": "send",
        "account_id": "63",
        "product_skus": [SKU]
    }
    s_resp = requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=headers, json=send_payload)
    print(f"Trigger result: {s_resp.text}")

if __name__ == "__main__":
    force_global_refresh()

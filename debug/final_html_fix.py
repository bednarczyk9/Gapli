import requests
import json
import os

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def final_html_fix():
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    
    html = resp.json().get("data", {}).get("custom_description", "")
    
    # The most primitive but effective fix for the reported error
    # Allegro is seeing <b> instead of </b> at the end of paragraphs.
    print(f"Original <b> count: {html.lower().count('<b>')}")
    print(f"Original </b> count: {html.lower().count('</b>')}")

    # Fix specific broken patterns
    fixed = html.replace(').<b></p>', ').</b></p>')
    fixed = fixed.replace('zestawu.<b></p>', 'zestawu.</b></p>')
    
    # Global balance check
    while fixed.lower().count('<b>') > fixed.lower().count('</b>'):
         # Find the last <b> and replace with </b>
         last_b = fixed.lower().rfind('<b>')
         if last_b == -1: break
         fixed = fixed[:last_b] + '</b>' + fixed[last_b+3:]
         
    print(f"New <b> count: {fixed.lower().count('<b>')}")
    print(f"New </b> count: {fixed.lower().count('</b>')}")

    # Save
    payload = resp.json()["data"]
    payload["custom_description"] = fixed
    up_url = "https://gapli.com/api/product-customizer/customizations"
    requests.post(up_url, headers=GAPLI_HEADERS, json=payload)
    
    # Force send
    api_key = os.environ.get("Gapli_Apikey")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=headers, json={
        "action": "send",
        "account_id": "63",
        "product_skus": [SKU]
    })
    print("Fixed and triggered.")

if __name__ == "__main__":
    final_html_fix()

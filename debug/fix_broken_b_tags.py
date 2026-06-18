import requests
import json
import os
import re

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def fix_sku_html_manual():
    # 1. Fetch current
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    
    data = resp.json().get("data", {})
    html = data.get("custom_description", "")
    
    # 2. Fix the broken <b><b> tags (often typo for </b>)
    # The snippet showed ".<b></p>" which should be ".</b></p>"
    fixed_html = html.replace(".<b></p>", ".</b></p>")
    fixed_html = fixed_html.replace(".<b></p>", ".</b></p>") # Repeat if multiple
    
    # 3. Use a more robust approach: close all open b tags
    # First, let's replace all <b> that are followed by </p> or </h2> or </h1> or </li> with </b>
    fixed_html = re.sub(r'<b>\s*(</p>|</h2>|</h1>|</li>)', r'</b>\1', fixed_html)
    
    # Count again
    open_b = fixed_html.lower().count('<b>')
    close_b = fixed_html.lower().count('</b>')
    print(f"Fixed counts - <b>: {open_b}, </b>: {close_b}")
    
    if open_b != close_b:
        print("STILL IMBALANCED! Forcing balance...")
        if open_b > close_b:
            fixed_html += "</b>" * (open_b - close_b)
            
    # 4. Save back to Gapli
    payload = {
        "sku": SKU,
        "scope": "user",
        "platform": "allegro",
        "custom_name": data.get("custom_name"),
        "custom_description": fixed_html,
        "is_active": True,
        "images_mode": "replace"
    }
    
    up_url = "https://gapli.com/api/product-customizer/customizations"
    up_resp = requests.post(up_url, headers=GAPLI_HEADERS, json=payload)
    print(f"Save Result: {up_resp.status_code}")
    
    # 5. Trigger resync for Skarbiec (63)
    api_key = os.environ.get("Gapli_Apikey")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    send_payload = {
        "action": "send",
        "account_id": "63",
        "product_skus": [SKU]
    }
    s_resp = requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=headers, json=send_payload)
    print(f"Marketplace Resync Result: {s_resp.text}")

if __name__ == "__main__":
    fix_sku_html_manual()

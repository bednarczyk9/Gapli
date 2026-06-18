import requests
import json
import os
import re

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def ultra_safe_fix():
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    
    html = resp.json().get("data", {}).get("custom_description", "")
    
    # Strategy: Strip ALL tags except <p> and <b>
    # Then ensure all <b> are closed.
    
    # 1. Strip all non-whitelisted tags
    clean_text = re.sub(r'</?(?!p|b|/p|/b)[a-z0-9]+(?:\s+[^>]*)?>', '', html, flags=re.IGNORECASE)
    
    # 2. Convert multiple spaces/newlines to single ones
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    # 3. Balance <b> tags using a stack
    parts = re.split(r'(</?b>)', clean_text, flags=re.IGNORECASE)
    balanced_parts = []
    is_open = False
    for p in parts:
        if p.lower() == '<b>':
            if is_open: balanced_parts.append('</b>') # Close nested
            balanced_parts.append('<b>')
            is_open = True
        elif p.lower() == '</b>':
            if is_open:
                balanced_parts.append('</b>')
                is_open = False
            else:
                pass # Ignore closing tag without opening
        else:
            balanced_parts.append(p)
    if is_open:
        balanced_parts.append('</b>')
        
    final_html = "".join(balanced_parts)
    
    # 4. Wrap in simple paragraphs if needed
    if not final_html.startswith('<p>'):
        final_html = f"<p>{final_html}</p>"

    # Save back
    payload = resp.json()["data"]
    payload["custom_description"] = final_html
    requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=payload)
    
    # Trigger Send
    api_key = os.environ.get("Gapli_Apikey")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    r = requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=headers, json={
        "action": "send",
        "account_id": "63",
        "product_skus": [SKU]
    })
    print(f"Ultra-safe fix result: {r.text}")

if __name__ == "__main__":
    ultra_safe_fix()

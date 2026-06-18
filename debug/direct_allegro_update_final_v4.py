import requests
import json
import base64
import re
import os

# Credentials provided by user for AlejaOkazji
CLIENT_ID = "429dd510a6714131bcc6359602f5df56"
CLIENT_SECRET = "U9uFj24fhXBXF1aSSfds2pgISUsvgKtxIRhel0RQu5tOBOFLjbgGOR8OAiA02aRe"

# Gapli Token for fetching customization
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = "1053851_131"
OFFER_ID = "18608416843"

TOKEN_FILE = "debug_allegro_access_token.txt"

def fetch_customization():
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        return resp.json().get("data")
    return None

def extreme_clean_html(html):
    if not html: return ""
    
    # 1. First, handle italics by replacing with bold
    html = re.sub(r'<(i|em)(\s+[^>]*)?>', '<b>', html, flags=re.IGNORECASE)
    html = re.sub(r'</(i|em)>', '</b>', html, flags=re.IGNORECASE)
    
    # 2. Allegro prefers <p> over <br>
    html = re.sub(r'<br\s*/?>', '</p><p>', html, flags=re.IGNORECASE)
    
    # 3. Strip ALL attributes from ALL tags
    html = re.sub(r'<([a-z0-9]+)\s+[^>]*>', r'<\1>', html, flags=re.IGNORECASE)

    # 4. Strip ALL tags EXCEPT the strictly allowed ones
    allowed = ['h1', 'h2', 'p', 'ul', 'ol', 'li', 'b']
    
    def tag_stripper(match):
        tag_full = match.group(0)
        tag_name_match = re.search(r'</?([a-z0-9]+)', tag_full.lower())
        if tag_name_match:
            tag_name = tag_name_match.group(1)
            if tag_name in allowed:
                return tag_full
        return ""
    
    html = re.sub(r'<[^>]+>', tag_stripper, html)
    
    # 5. FIX TAG BALANCING for <b> (The common failure point)
    # Strategy: remove all <b> and </b> then re-apply based on counts, 
    # but better: just ensure every <b> has a </b> and no nested <b><b>
    
    # Remove nested <b><b>...</b></b>
    html = re.sub(r'<b>\s*<b>', '<b>', html, flags=re.IGNORECASE)
    html = re.sub(r'</b>\s*</b>', '</b>', html, flags=re.IGNORECASE)
    
    # Count balance
    open_tags = len(re.findall(r'<b>', html, flags=re.IGNORECASE))
    close_tags = len(re.findall(r'</b>', html, flags=re.IGNORECASE))
    
    if open_tags > close_tags:
        html += '</b>' * (open_tags - close_tags)
    elif close_tags > open_tags:
        # Very hard to fix safely without a parser, let's just strip and hope for the best
        # or just add more open tags at the start? No. 
        # Let's try to remove trailing closing tags.
        for _ in range(close_tags - open_tags):
            html = re.sub(r'</b>$', '', html.strip(), flags=re.IGNORECASE)

    # 6. Final cleanup of empty paragraphs
    html = html.replace('<p></p>', '').replace('<p> </p>', '')
    
    return html

def update_allegro_offer(token, cust_data):
    url = f"https://api.allegro.pl/sale/product-offers/{OFFER_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "Content-Type": "application/vnd.allegro.public.v1+json"
    }
    
    name = cust_data.get("custom_name")
    raw_desc = cust_data.get("custom_description")
    clean_desc = extreme_clean_html(raw_desc)
    
    patch_data = {
        "name": name[:50],
        "description": {
            "sections": [
                {
                    "items": [
                        {
                            "type": "TEXT",
                            "content": clean_desc
                        }
                    ]
                }
            ]
        }
    }
    
    resp = requests.patch(url, headers=headers, json=patch_data)
    print(f"Result ({resp.status_code}):")
    if resp.status_code in [200, 204, 201]:
        print("SUCCESS! Offer updated.")
    else:
        print(resp.text)

if __name__ == "__main__":
    if os.path.exists(TOKEN_FILE):
         with open(TOKEN_FILE, "r") as f:
             token = f.read().strip()
         cust = fetch_customization()
         if cust and token:
             update_allegro_offer(token, cust)

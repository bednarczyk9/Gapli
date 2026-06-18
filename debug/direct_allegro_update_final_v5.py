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

def atomic_clean_html(html):
    if not html: return ""
    
    # 1. Strip ALL tags first (keep content)
    # This is the safest way to ensure no broken tags remain.
    # We will then re-wrap sections in paragraphs.
    
    # Replace common block tags with newlines to preserve structure
    html = re.sub(r'</?(p|h1|h2|li|div|br)[^>]*>', '\n', html, flags=re.IGNORECASE)
    
    # Strip all other tags
    clean_text = re.sub(r'<[^>]+>', '', html)
    
    # Normalize whitespace
    lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
    
    # Reconstruct as simple paragraphs
    # Allegro only needs <p> and <b>
    final_html = ""
    for line in lines:
        # If it's a heading-like line (short, maybe all caps), make it bold
        if len(line) < 100 and (line.isupper() or line.endswith(':')):
             final_html += f"<p><b>{line}</b></p>"
        else:
             final_html += f"<p>{line}</p>"
             
    return final_html

def update_allegro_offer(token, cust_data):
    url = f"https://api.allegro.pl/sale/product-offers/{OFFER_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "Content-Type": "application/vnd.allegro.public.v1+json"
    }
    
    name = cust_data.get("custom_name")
    raw_desc = cust_data.get("custom_description")
    
    # Atomic clean: remove everything and rebuild
    clean_desc = atomic_clean_html(raw_desc)
    
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
        print("SUCCESS! Offer updated with atomic-cleaned description.")
    else:
        print(resp.text)

if __name__ == "__main__":
    if os.path.exists(TOKEN_FILE):
         with open(TOKEN_FILE, "r") as f:
             token = f.read().strip()
         cust = fetch_customization()
         if cust and token:
             update_allegro_offer(token, cust)
    else:
        print("No token file found.")

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

def get_token_from_code(code):
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    url = "https://allegro.pl/auth/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:8000"
    }
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        return token
    else:
        print(f"Token Error: {resp.status_code} {resp.text}")
        if os.path.exists(TOKEN_FILE):
             with open(TOKEN_FILE, "r") as f:
                 return f.read()
    return None

def fetch_customization():
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        return resp.json().get("data")
    return None

def clean_html_for_allegro(html):
    if not html: return ""
    # Allegro allows only: h1, h2, p, ul, ol, li, b
    # Fix italics (<i>)
    html = re.sub(r'</?i>', '<b>', html)
    # Remove spans, divs etc.
    html = re.sub(r'</?(span|div|section|article|header|footer)[^>]*>', '', html)
    # Convert <br> to <p>
    html = html.replace('<br>', '</p><p>').replace('<br/>', '</p><p>').replace('<br />', '</p><p>')
    # Strip any other tags (very simplified)
    return html

def update_allegro_offer(token, cust_data):
    if not cust_data:
        print("No customization data.")
        return
        
    url = f"https://api.allegro.pl/sale/product-offers/{OFFER_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "Content-Type": "application/vnd.allegro.public.v1+json"
    }
    
    name = cust_data.get("custom_name")
    raw_desc = cust_data.get("custom_description")
    clean_desc = clean_html_for_allegro(raw_desc)
    
    # Allegro limit: 50 chars for title usually
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
    
    print(f"Sending final PATCH to {url}...")
    resp = requests.patch(url, headers=headers, json=patch_data)
    print(f"Result ({resp.status_code}): {resp.text[:500]}")
    if resp.status_code in [200, 204, 201]:
        print("SUCCESS!")

if __name__ == "__main__":
    import sys
    code = sys.argv[1] if len(sys.argv) > 1 else None
    token = get_token_from_code(code) if code else None
    if not token and os.path.exists(TOKEN_FILE):
         with open(TOKEN_FILE, "r") as f:
             token = f.read()
             
    if token:
        cust = fetch_customization()
        update_allegro_offer(token, cust)
    else:
        print("No valid token.")

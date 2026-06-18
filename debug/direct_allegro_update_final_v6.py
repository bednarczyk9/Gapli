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
    print(f"Exchanging code for token...")
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
    return None

def fetch_customization():
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        return resp.json().get("data")
    return None

def extreme_clean_v2(html):
    if not html: return ""
    # Remove all italics first as they are the biggest problem
    html = re.sub(r'</?i(?:\s+[^>]*)?>', '', html, flags=re.IGNORECASE)
    # Strip all attributes from tags
    html = re.sub(r'<([a-z0-9]+)\s+[^>]*>', r'<\1>', html, flags=re.IGNORECASE)
    # Filter only allowed tags
    allowed = ['h1', 'h2', 'p', 'ul', 'ol', 'li', 'b']
    def filter_tags(match):
        tag = match.group(0)
        name = re.search(r'</?([a-z0-9]+)', tag.lower()).group(1)
        return tag if name in allowed else ""
    html = re.sub(r'<[^>]+>', filter_tags, html)
    # Ensure balancing by closing all open b tags at the end
    # (Simplified: just remove all <b> and </b> and re-wrap important stuff if needed, 
    # but let's try to just strip ALL <b> tags to be 100% safe for this attempt)
    html = re.sub(r'</?b>', '', html, flags=re.IGNORECASE)
    return html

def update_allegro_offer(token, cust_data):
    url = f"https://api.allegro.pl/sale/product-offers/{OFFER_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "Content-Type": "application/vnd.allegro.public.v1+json"
    }
    name = cust_data.get("custom_name")
    desc = extreme_clean_v2(cust_data.get("custom_description"))
    patch_data = {"name": name[:50], "description": {"sections": [{"items": [{"type": "TEXT", "content": desc}]}]}}
    resp = requests.patch(url, headers=headers, json=patch_data)
    print(f"PATCH Result ({resp.status_code}): {resp.text}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        code = sys.argv[1]
        token = get_token_from_code(code)
        if token:
            cust = fetch_customization()
            update_allegro_offer(token, cust)
    else:
        print("Need code.")

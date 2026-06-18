import requests
import json
import os
import re

# Credentials from previous successful attempt
CLIENT_ID = "429dd510a6714131bcc6359602f5df56"
CLIENT_SECRET = "U9uFj24fhXBXF1aSSfds2pgISUsvgKtxIRhel0RQu5tOBOFLjbgGOR8OAiA02aRe"
TOKEN_FILE = "debug_allegro_access_token.txt"

# Gapli Token
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = "1053851_131"
OFFER_ID = "18608416843"

def fetch_cleaned_customization():
    print(f"Fetching LATEST CLEANED customization from Gapli for {SKU}...")
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        return resp.json().get("data")
    return None

def force_push_to_allegro():
    if not os.path.exists(TOKEN_FILE):
        print("Error: No saved token found. Please re-authorize.")
        return
        
    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()
        
    cust = fetch_cleaned_customization()
    if not cust:
        print("Failed to fetch data from Gapli.")
        return
        
    print(f"Pushing to Allegro {OFFER_ID}...")
    url = f"https://api.allegro.pl/sale/product-offers/{OFFER_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "Content-Type": "application/vnd.allegro.public.v1+json"
    }
    
    # We'll use the description directly as it was cleaned in the previous step
    name = cust.get("custom_name")
    desc = cust.get("custom_description")
    
    # Final safety check for Allegro tags
    # Allegro allows: h1, h2, p, ul, ol, li, b
    # Let's ensure no stray <i> tags remain
    desc = re.sub(r'</?i>', '<b>', desc)
    
    payload = {
        "name": name,
        "description": {
            "sections": [
                {
                    "items": [
                        {
                            "type": "TEXT",
                            "content": desc
                        }
                    ]
                }
            ]
        }
    }
    
    resp = requests.patch(url, headers=headers, json=payload)
    print(f"Allegro Response ({resp.status_code}):")
    if resp.status_code in [200, 204, 201]:
        print("SUCCESS! Description updated on Allegro.")
    else:
        print(resp.text)

if __name__ == "__main__":
    force_push_to_allegro()

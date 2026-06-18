import requests
import json
import os
import base64
import time

# Credentials provided by user for AlejaOkazji
CLIENT_ID = "429dd510a6714131bcc6359602f5df56"
CLIENT_SECRET = "U9uFj24fhXBXF1aSSfds2pgISUsvgKtxIRhel0RQu5tOBOFLjbgGOR8OAiA02aRe"

# Gapli Token for fetching customization
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = "1053851_131"
OFFER_ID = "18608416843"

def get_auth_url():
    # Redirect URI must match what's registered in Allegro Apps (usually localhost:8000 in this project)
    redirect_uri = "http://localhost:8000"
    url = f"https://allegro.pl/auth/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={redirect_uri}"
    return url

def get_token_from_code(code):
    print(f"Exchanging code {code} for token...")
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
        return resp.json()
    else:
        print(f"Failed to get token: {resp.status_code} {resp.text}")
        return None

def fetch_customization():
    print(f"Fetching customization from Gapli for {SKU}...")
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        return resp.json().get("data")
    return None

def update_allegro_offer(token, cust_data):
    if not cust_data:
        print("No customization data to push.")
        return
        
    print(f"Updating Allegro offer {OFFER_ID} directly...")
    
    url = f"https://api.allegro.pl/sale/product-offers/{OFFER_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "Content-Type": "application/vnd.allegro.public.v1+json"
    }
    
    # First GET
    curr_resp = requests.get(url, headers=headers)
    if curr_resp.status_code != 200:
        print(f"Failed to fetch current offer state: {curr_resp.status_code} {curr_resp.text}")
        return
        
    offer = curr_resp.json()
    
    # Update name and description
    offer["name"] = cust_data.get("custom_name", offer["name"])
    
    html_desc = cust_data.get("custom_description")
    if html_desc:
        offer["description"] = {
            "sections": [
                {
                    "items": [
                        {
                            "type": "TEXT",
                            "content": html_desc
                        }
                    ]
                }
            ]
        }
    
    # Try PATCH
    patch_data = {
        "name": offer["name"],
        "description": offer["description"]
    }
    
    resp = requests.patch(url, headers=headers, json=patch_data)
    print(f"PATCH Response ({resp.status_code}):")
    if resp.status_code not in [200, 204, 201]:
        print(resp.text)
        # Try PUT
        print("Trying PUT...")
        resp = requests.put(url, headers=headers, json=offer)
        print(f"PUT Response ({resp.status_code}):")
        if resp.status_code not in [200, 204, 201]:
             print(resp.text)
    else:
        print("Update successful via PATCH.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        code = sys.argv[1]
        tokens = get_token_from_code(code)
        if tokens:
            access_token = tokens.get("access_token")
            cust = fetch_customization()
            if cust:
                update_allegro_offer(access_token, cust)
    else:
        print(f"Please go to this URL to authorize:\n\n{get_auth_url()}\n")
        print("After authorizing, paste the 'code' from the redirect URL as an argument to this script.")

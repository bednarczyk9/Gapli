import requests
import json
import os
import base64
import time

# Use the refresh token logic from pipeline/clean_skarbiec_drafts.py
CLIENT_ID = "429dd510a6714131bcc6359602f5df56"
CLIENT_SECRET = "U9uFj24fhXBXF1aSSfds2pgISUsvgKtxIRhel0RQu5tOBOFLjbgGOR8OAiA02aRe"
REFRESH_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2FsbGVncm8ucGwiLCJ1c2VyX25hbWUiOiIxMTg0MjM5ODAiLCJzY29wZSI6WyJhbGxlZ3JvOmFwaTpvcmRlcnM6cmVhZCIsImFsbGVncm86YXBpOmZ1bGZpbGxtZW50OnJlYWQiLCJhbGxlZ3JvOmFwaTpwcm9maWxlOndyaXRlIiwiYWxsZWdybzphcGk6c2FsZTpvZmZlcnM6d3JpdGUiLCJhbGxlZ3JvOmFwaTpmdWxmaWxsbWVudDp3cml0ZSIsImFsbGVncm86YXBpOmJpbGxpbmc6cmVhZCIsImFsbGVncm86YXBpOmNhbXBhaWducyIsImFsbGVncm86YXBpOmRpc3B1dGVzIiwiYWxsZWdybzphcGk6YWZmaWxpYXRlOndyaXRlIiwiYWxsZWdybzphcGk6c2FsZTpvZmZlcnM6cmVhZCIsImFsbGVncm86YXBpOmJpZHMiLCJhbGxlZ3JvOmFwaTpzaGlwbWVudHM6d3JpdGUiLCJhbGxlZ3JvOmFwaTpvcmRlcnM6d3JpdGUiLCJhbGxlZ3JvOmFwaTphZHMiLCJhbGxlZ3JvOmFwaTpwYXltZW50czp3cml0ZSIsImFsbGVncm86YXBpOnNhbGU6c2V0dGluZ3M6d3JpdGUiLCJhbGxlZ3JvOmFwaTpwcm9maWxlOnJlYWQiLCJhbGxlZ3JvOmFwaTpyYXRpbmdzIiwiYWxsZWdybzphcGk6YWZmaWxpYXRlOnJlYWQiLCJhbGxlZ3JvOmFwaTpzYWxlOnNldHRpbmdzOnJlYWQiLCJhbGxlZ3JvOmFwaTpwYXltZW50czpyZWFkIiwiYWxsZWdybzphcGk6c2hpcG1lbnRzOnJlYWQiLCJhbGxlZ3JvOmFwaTptZXNzYWdpbmciXSwiYXRpIjoiMzY4ODQwNmQtNjYyMS00NDQ2LTk3MWMtOWIzZjY0ZTE1NjdiIiwiYWxsZWdyb19hcGkiOnRydWUsImV4cCI6MTc4ODU2MDY3NywiY2xpZW50X2lkIjoiNWI2ZTc4MWZmZjJhNDY0NmI4ZDE4ODU2MDdmMWZhOWUiLCJqdGkiOiIzZGY2MjliMi04YWVmLTQ3NTQtYjhiYS02ZjcwZjY5NTA4NmMifQ.fEbPN08j7-3BVNemcFcuSYMo1vKOs-EdwLZFQTl9I5TRo8EHJbUz-ExNXyn5cZARxO911CJHbmTgNYhVxz1yj8GjifC4qRZN_wbOGpVMd3MdEjR4btKnX9GQVqCvnbe066BPbAZ2qhfA6iKbhZ36ppiBbI190Sh-c5NVlSZvj6WHLwwkwP7UxUnZ5REfwXcxoUNW2ECSnT9UaxbfPpSVovRMPbxLCsqbMwSIXnLW3kpRn_6gy-ywRvRKT67Y7onOnnC098hAwqtSxg3p9GAtxvfXgvQYpT2M2Xzz_qH6zTozREWwizwzFemMc-MwtB7IJD9Yom6VVT4XTc-B2rJiBw"

# Gapli Token for fetching customization
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = "1053851_131"
OFFER_ID = "18608416843"

def refresh_token():
    print("Refreshing Allegro token...")
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    url = "https://allegro.pl/auth/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code == 200:
        return resp.json().get("access_token")
    else:
        print(f"Failed to refresh token: {resp.status_code} {resp.text}")
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
        
    print(f"Updating Allegro offer {OFFER_ID} directly using REFRESHED TOKEN...")
    
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
    token = refresh_token()
    if token:
        cust = fetch_customization()
        if cust:
            update_allegro_offer(token, cust)
        else:
            print("Failed to fetch Gapli customization.")
    else:
        print("Failed to get refreshed token.")

import requests
import json
import os
import base64
import time

# Use the TOKEN from allegro_token.json which is a user token
TOKEN_FILE = "allegro_token.json"

# Gapli Token for fetching customization
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = "1053851_131"
OFFER_ID = "18608416843"

def get_user_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        data = json.load(f)
        return data.get("access_token")

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
        
    print(f"Updating Allegro offer {OFFER_ID} directly using USER TOKEN...")
    
    url = f"https://api.allegro.pl/sale/product-offers/{OFFER_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "Content-Type": "application/vnd.allegro.public.v1+json"
    }
    
    # First GET to have the full current state
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
        # If PATCH fails, try PUT
        print("Trying PUT...")
        resp = requests.put(url, headers=headers, json=offer)
        print(f"PUT Response ({resp.status_code}):")
        if resp.status_code not in [200, 204, 201]:
             print(resp.text)
    else:
        print("Update successful via PATCH.")

if __name__ == "__main__":
    token = get_user_token()
    if token:
        cust = fetch_customization()
        if cust:
            update_allegro_offer(token, cust)
        else:
            print("Failed to fetch Gapli customization.")
    else:
        print("Failed to get USER token from file.")

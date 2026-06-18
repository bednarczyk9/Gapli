import requests
import json
import os
import base64
import time

# Credentials provided by user
CLIENT_ID = "429dd510a6714131bcc6359602f5df56"
CLIENT_SECRET = "U9uFj24fhXBXF1aSSfds2pgISUsvgKtxIRhel0RQu5tOBOFLjbgGOR8OAiA02aRe"

# Gapli Token for fetching customization
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = "1053851_131"
OFFER_ID = "18608416843"

def get_allegro_token():
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    url = "https://allegro.pl/auth/oauth/token?grant_type=client_credentials"
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/vnd.allegro.public.v1+json"
    }
    
    resp = requests.post(url, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("access_token")
    else:
        print(f"Failed to get Allegro token: {resp.status_code} {resp.text}")
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
    
    # We use the product-offers API
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
    
    # Apply parameters from customization if possible
    cust_params = cust_data.get("custom_parameters", {})
    if cust_params:
        # We need to map custom_parameters to Allegro parameters
        # For simplicity, we'll keep existing params and only overwrite those that match by name
        # Actually, Allegro API usually prefers IDs.
        pass

    # Try PATCH instead of PUT if possible for partial update, 
    # but product-offers supports PATCH too.
    # Let's try PATCH first as it's safer for partial updates.
    patch_data = {
        "name": offer["name"],
        "description": offer["description"]
    }
    
    resp = requests.patch(url, headers=headers, json=patch_data)
    print(f"PATCH Response ({resp.status_code}):")
    if resp.status_code not in [200, 204, 201]:
        print(resp.text)
        # If PATCH fails, try PUT with the full object
        print("Trying PUT...")
        resp = requests.put(url, headers=headers, json=offer)
        print(f"PUT Response ({resp.status_code}):")
        if resp.status_code not in [200, 204, 201]:
             print(resp.text)
    else:
        print("Update successful via PATCH.")

if __name__ == "__main__":
    token = get_allegro_token()
    if token:
        cust = fetch_customization()
        if cust:
            update_allegro_offer(token, cust)
        else:
            print("Failed to fetch Gapli customization.")
    else:
        print("Failed to get Allegro token.")

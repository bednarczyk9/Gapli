import requests
import os
import base64
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLIENT_ID = os.environ.get("skarbiec_client_id")
CLIENT_SECRET = os.environ.get("skarbiec_client_secret")

def get_allegro_token():
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    url = "https://allegro.pl/auth/oauth/token?grant_type=client_credentials"
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/vnd.allegro.public.v1+json"
    }
    
    resp = requests.post(url, headers=headers)
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        logger.info("Successfully obtained Allegro Client Credentials token.")
        return token
    else:
        logger.error(f"Failed to get Allegro token: {resp.status_code} {resp.text}")
        return None

def get_category_parameters(cat_id, token):
    url = f"https://api.allegro.pl/sale/categories/{cat_id}/parameters"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("parameters", [])
    else:
        logger.error(f"Failed to fetch parameters: {resp.status_code}")
        return []

def analyze_required_params(cat_id):
    token = get_allegro_token()
    if not token: return
    
    params = get_category_parameters(cat_id, token)
    required = []
    
    print(f"\n--- Mandatory Parameters for Category {cat_id} ---")
    for p in params:
        if p.get("required"):
            options = ""
            if p.get("dictionary"):
                options = f" [Options: {', '.join([d['value'] for d in p['dictionary'][:5]])}...]"
            
            print(f"Name: {p['name']} (ID: {p['id']}) {options}")
            required.append({
                "name": p["name"],
                "id": p["id"],
                "options": [d["value"] for d in p.get("dictionary", [])]
            })
    return required

if __name__ == "__main__":
    # Test for 'Wieszaki łazienkowe' category
    analyze_required_params("112733")

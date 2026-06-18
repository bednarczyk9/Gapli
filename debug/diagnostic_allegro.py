import requests
import json
import base64
import os

# Credentials provided by user for AlejaOkazji
CLIENT_ID = "429dd510a6714131bcc6359602f5df56"
CLIENT_SECRET = "U9uFj24fhXBXF1aSSfds2pgISUsvgKtxIRhel0RQu5tOBOFLjbgGOR8OAiA02aRe"

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
        return resp.json().get("access_token")
    return None

def check_offer_and_me(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    
    # Check current user
    me_resp = requests.get("https://api.allegro.pl/me", headers=headers)
    print(f"Logged in as: {me_resp.json().get('login') if me_resp.status_code == 200 else me_resp.text}")
    
    # Check offer
    offer_resp = requests.get(f"https://api.allegro.pl/sale/product-offers/{OFFER_ID}", headers=headers)
    print(f"Offer {OFFER_ID} access status: {offer_resp.status_code}")
    if offer_resp.status_code != 200:
        print(offer_resp.text)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        token = get_token_from_code(sys.argv[1])
        if token:
            check_offer_and_me(token)

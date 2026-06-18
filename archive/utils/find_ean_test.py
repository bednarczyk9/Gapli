import requests
import os
import base64
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
    return resp.json().get("access_token")

def search_cheapest_by_ean(ean, token):
    url = "https://api.allegro.pl/offers/listing"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    # Search by EAN phrase and sort by price ascending
    params = {
        "phrase": ean,
        "sort": "+price", # price ascending
        "limit": 10
    }
    
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", {}).get("regular", [])
        # Also check promoted items if they are cheaper? Usually regular is enough.
        # promoted = data.get("items", {}).get("promoted", [])
        
        if not items:
            return None
            
        # Filter out user's own offers if needed? 
        # For now, let's just see all results.
        cheapest = items[0]
        price = cheapest.get("sellingMode", {}).get("price", {}).get("amount")
        seller = cheapest.get("seller", {}).get("id")
        return {"price": price, "seller_id": seller, "name": cheapest.get("name")}
    else:
        print(f"Error searching for {ean}: {resp.status_code} {resp.text}")
        return None

if __name__ == "__main__":
    token = get_allegro_token()
    ean = "5903890632663" # Deska SUP
    result = search_cheapest_by_ean(ean, token)
    print(f"Result for {ean}: {result}")

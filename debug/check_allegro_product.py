import requests
import os
import base64
import json

# Try to get credentials from env
CLIENT_ID = os.environ.get("alejaokazji_id")
CLIENT_SECRET = os.environ.get("alejaokazji_secret")

PRODUCT_ID = "a9dac6a4-c55a-4b0c-a06a-399d79f56d60"

def get_allegro_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: CLIENT_ID or CLIENT_SECRET not found.")
        return None
    
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

def check_allegro_product(token):
    url = f"https://api.allegro.pl/sale/products/{PRODUCT_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    
    resp = requests.get(url, headers=headers)
    print(f"Allegro product check ({resp.status_code}):")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Name: {data.get('name')}")
        print(f"Category: {data.get('category', {}).get('id')}")
    else:
        print(resp.text)

if __name__ == "__main__":
    token = get_allegro_token()
    if token:
        check_allegro_product(token)

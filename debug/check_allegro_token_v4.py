import requests
import json
import time

TOKEN_FILE = "debug_allegro_access_token.txt"

def check_token_and_list():
    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    
    # Try to get profile to check token
    resp = requests.get("https://api.allegro.pl/me", headers=headers)
    if resp.status_code != 200:
        print(f"Token invalid or expired: {resp.status_code} {resp.text}")
        return
    
    me = resp.json()
    print(f"Logged in as: {me.get('login')} (ID: {me.get('id')})")
    
    # List inactive offers (Drafts and Ended)
    # limit=1000 is max for some endpoints, but usually it's 100 or 1000
    # publication.status=INACTIVE
    url = "https://api.allegro.pl/sale/offers?publication.status=INACTIVE&limit=100"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        total = data.get("totalCount")
        print(f"Total inactive offers: {total}")
        offers = data.get("offers", [])
        for o in offers[:10]:
            print(f" - {o.get('id')}: {o.get('name')} (Status: {o.get('publication', {}).get('status')})")
    else:
        print(f"Failed to list offers: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    check_token_and_list()

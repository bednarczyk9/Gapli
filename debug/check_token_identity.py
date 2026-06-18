import requests
import json
import os

TOKEN_FILE = "allegro_token.json"

def check_identity():
    if not os.path.exists(TOKEN_FILE):
        print("Token file not found.")
        return
    
    with open(TOKEN_FILE, "r") as f:
        tokens = json.load(f)
    
    token = tokens.get("access_token")
    if not token:
        print("No access token in file.")
        return
        
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    
    resp = requests.get("https://api.allegro.pl/me", headers=headers)
    if resp.status_code == 200:
        me = resp.json()
        print(f"Token belongs to user: {me.get('login')} (ID: {me.get('id')})")
    else:
        print(f"Failed to check identity: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    check_identity()

import requests
import json
import os

TOKEN_FILE = "allegro_token.json"

def get_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        data = json.load(f)
        return data.get("access_token")

def check_account():
    token = get_token()
    if not token:
        print("Token not found.")
        return
        
    url = "https://api.allegro.pl/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Logged in as: {data.get('login')}")
    else:
        print(f"Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    check_account()

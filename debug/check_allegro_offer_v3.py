import requests
import json
import os

TOKEN_FILE = "allegro_token.json"
AUCTION_ID = "18608416843"

def get_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        data = json.load(f)
        return data.get("access_token")

def check_allegro_offer():
    token = get_token()
    if not token:
        print("Token not found.")
        return
        
    url = f"https://api.allegro.pl/sale/product-offers/{AUCTION_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Name: {data.get('name')}")
        print(f"Status: {data.get('publication', {}).get('status')}")
        print("\nDescription:")
        desc = data.get("description", {})
        sections = desc.get("sections", [])
        for i, section in enumerate(sections):
            for item in section.get("items", []):
                if item.get("type") == "TEXT":
                    print(f"Section {i} TEXT: {item.get('content')[:200]}...")
        
        print("\nParameters:")
        for p in data.get("parameters", []):
            print(f"- {p.get('name')}: {p.get('valuesLabels')}")
            
    else:
        print(f"Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    check_allegro_offer()

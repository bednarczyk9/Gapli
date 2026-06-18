import requests
import base64
import os
import json

def get_allegro_token():
    client_id = os.environ.get("skarbiec_client_id")
    client_secret = os.environ.get("skarbiec_client_secret")
    if not client_id or not client_secret:
        try:
            with open(".env", "r") as f:
                for line in f:
                    if "skarbiec_client_id=" in line:
                        client_id = line.split("=")[1].strip().strip('"')
                    if "skarbiec_client_secret=" in line:
                        client_secret = line.split("=")[1].strip().strip('"')
        except:
            pass
    if not client_id or not client_secret: return None
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    url = "https://allegro.pl/auth/oauth/token?grant_type=client_credentials"
    headers = {"Authorization": f"Basic {auth_header}"}
    resp = requests.post(url, headers=headers)
    return resp.json().get("access_token") if resp.status_code == 200 else None

def get_category_params(cat_id, token):
    url = f"https://api.allegro.pl/sale/categories/{cat_id}/parameters"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.allegro.public.v1+json"}
    resp = requests.get(url, headers=headers)
    return resp.json()

if __name__ == "__main__":
    token = get_allegro_token()
    if token:
        params = get_category_params("258919", token)
        for p in params.get("parameters", []):
            if p['id'] == "248811":
                print(f"Parameter: {p['name']}")
                for d in p['dictionary']:
                    if "peekaboo" in d['value'].lower():
                        print(f"Found: {d['value']} (ID: {d['id']})")

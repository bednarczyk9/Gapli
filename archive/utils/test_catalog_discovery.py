import requests
import os
import base64

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

def search_product_by_ean(ean, token):
    url = "https://api.allegro.pl/sale/products"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    params = {"ean": ean}
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"Error searching product {ean}: {resp.status_code} {resp.text}")
        return None

if __name__ == "__main__":
    token = get_allegro_token()
    ean = "5903890632663"
    result = search_product_by_ean(ean, token)
    import json
    print(json.dumps(result, indent=2))

import requests, base64, os, json, sys

def get_allegro_token():
    # Use hit_bazar or skarbiec for general searches
    client_id = os.environ.get("hit_bazar_client_id")
    client_secret = os.environ.get("hit_bazar_client_secret")
    if not client_id:
        client_id = os.environ.get("skarbiec_client_id")
        client_secret = os.environ.get("skarbiec_client_secret")
        
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    url = "https://allegro.pl/auth/oauth/token?grant_type=client_credentials"
    resp = requests.post(url, headers={"Authorization": f"Basic {auth_header}"})
    return resp.json().get("access_token")

def search_product(gtin):
    token = get_allegro_token()
    url = f"https://api.allegro.pl/sale/products?gtin={gtin}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.allegro.public.v1+json"}
    resp = requests.get(url, headers=headers)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    search_product(sys.argv[1] if len(sys.argv) > 1 else "5904726003527")

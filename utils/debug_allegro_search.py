import requests
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN_FILE = "allegro_token.json"

def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f).get("access_token")
    return None

def debug_search(ean):
    token = get_token()
    if not token:
        print("Brak tokena! Uruchom najpierw główny skrypt.")
        return

    url = "https://api.allegro.pl/offers/listing"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    
    # Próba 1: Standardowe wyszukiwanie po frazie (tak jak w skrypcie)
    params_phrase = {"phrase": ean, "fallback": "false"}
    print(f"\n--- Test dla EAN: {ean} ---")
    print(f"Próba 1 (phrase={ean}):")
    resp = requests.get(url, headers=headers, params=params_phrase)
    if resp.status_code == 200:
        data = resp.json()
        regular = data.get("items", {}).get("regular", [])
        promoted = data.get("items", {}).get("promoted", [])
        print(f"  Znalazłem: Regularne: {len(regular)}, Promowane: {len(promoted)}")
        if regular:
            print(f"  Najtańsza cena (regular): {regular[0]['sellingMode']['price']['amount']}")
    else:
        print(f"  Błąd API: {resp.status_code} {resp.text}")

    # Próba 2: Wyszukiwanie z włączonym fallback (może EAN jest w parametrach, a nie w tytule)
    params_fallback = {"phrase": ean, "fallback": "true"}
    print(f"Próba 2 (phrase={ean}, fallback=true):")
    resp = requests.get(url, headers=headers, params=params_fallback)
    if resp.status_code == 200:
        data = resp.json()
        regular = data.get("items", {}).get("regular", [])
        print(f"  Znalazłem: Regularne: {len(regular)}")
    
    # Próba 3: Wyszukiwanie po parametrze EAN (jeśli Allegro to wspiera w listingu)
    # listing nie wspiera bezpośrednio filtra ean, ale sprawdźmy czy 'phrase' bez cudzysłowu działa inaczej
    params_strict = {"phrase": f'"{ean}"'}
    print(f"Próba 3 (phrase=\"{ean}\"):")
    resp = requests.get(url, headers=headers, params=params_strict)
    if resp.status_code == 200:
        data = resp.json()
        regular = data.get("items", {}).get("regular", [])
        print(f"  Znalazłem: Regularne: {len(regular)}")

if __name__ == "__main__":
    # Testujemy pierwsze dwa EAN-y z Twojej listy
    debug_search("5711724080203")
    debug_search("5901969429848")

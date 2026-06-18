import requests
import os
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Wymagamy refresh token z pliku
TOKEN_FILE = "allegro_token.json"
CLIENT_ID = os.environ.get("skarbiec_client_id")
CLIENT_SECRET = os.environ.get("skarbiec_client_secret")

def refresh_access_token():
    if not os.path.exists(TOKEN_FILE):
        logger.error(f"Nie znaleziono pliku {TOKEN_FILE}.")
        return None
    
    with open(TOKEN_FILE, "r") as f:
        tokens = json.load(f)
    
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        logger.error("Brak refresh_token w pliku.")
        return None
        
    logger.info("Odświeżanie tokena z Allegro API...")
    url = "https://allegro.pl/auth/oauth/token"
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    import base64
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    
    headers = {"Authorization": f"Basic {auth_b64}"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code == 200:
        new_tokens = resp.json()
        with open(TOKEN_FILE, "w") as f:
            json.dump(new_tokens, f)
        logger.info("Token odświeżony i zapisany pomyślnie.")
        return new_tokens.get("access_token")
    else:
        logger.error(f"Błąd odświeżania tokena: {resp.status_code} {resp.text}")
        return None

def fetch_inactive_offers(token, limit=1000):
    """Pobiera listę szkiców i zakończonych ofert."""
    logger.info("Pobieranie listy nieaktywnych ofert (szkiców)...")
    url = f"https://api.allegro.pl/sale/offers?publication.status=INACTIVE&limit={limit}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        offers = resp.json().get("offers", [])
        logger.info(f"Znaleziono {len(offers)} nieaktywnych ofert.")
        return [o["id"] for o in offers]
    else:
        logger.error(f"Błąd pobierania ofert: {resp.status_code} {resp.text}")
        return []

def delete_offers(token, offer_ids):
    """Próbuje usunąć wybrane oferty (jeśli są szkicami lub da się je usunąć)."""
    if not offer_ids:
        return
        
    logger.info(f"Rozpoczynam usuwanie {len(offer_ids)} ofert...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }
    
    success_count = 0
    fail_count = 0
    
    for oid in offer_ids:
        url = f"https://api.allegro.pl/sale/offers/{oid}"
        # Najpierw sprawdzamy status, czy to szkic (INACTIVE)
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            offer = resp.json()
            if offer.get("publication", {}).get("status") == "INACTIVE":
                 del_resp = requests.delete(url, headers=headers)
                 if del_resp.status_code == 204:
                     success_count += 1
                     if success_count % 10 == 0:
                         logger.info(f"Usunięto {success_count} ofert...")
                 else:
                     logger.warning(f"Nie można usunąć oferty {oid}: {del_resp.status_code}")
                     fail_count += 1
            else:
                 logger.debug(f"Oferta {oid} nie jest w statusie INACTIVE (szkic). Pomiń.")
        else:
             logger.warning(f"Nie można pobrać oferty {oid}: {resp.status_code} {resp.text}")
             
        time.sleep(0.1) # Lekki sleep by nie dusić API (10 req/sec)

    logger.info(f"Zakończono. Usunięto: {success_count}, Błędy: {fail_count}")

def main():
    token = refresh_access_token()
    if not token:
        return
        
    # Ponieważ pobieramy po 1000 sztuk max, możemy zrobić pętlę
    for i in range(5): # Spróbuj usunąć do 5000 w 5 pętlach
        offer_ids = fetch_inactive_offers(token, limit=1000)
        if not offer_ids:
            logger.info("Brak więcej szkiców do usunięcia.")
            break
        
        delete_offers(token, offer_ids)
        time.sleep(2)

if __name__ == "__main__":
    main()

import os
import json
import logging
import time
import requests
import pandas as pd
from datetime import datetime

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CLIENT_ID = os.environ.get("skarbiec_client_id")
CLIENT_SECRET = os.environ.get("skarbiec_client_secret")
REDIRECT_URI = "http://localhost:8000" # Allegro still needs this defined in app
TOKEN_FILE = "allegro_token.json"

class AllegroAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None

    def manual_auth(self):
        """Używa ręcznego kopiowania kodu - najpewniejsza metoda."""
        auth_url = f"https://allegro.pl/auth/oauth/authorize?response_type=code&client_id={self.client_id}&redirect_uri={REDIRECT_URI}"
        
        print("\n" + "="*80)
        print("KROK 1: Otwórz poniższy link w przeglądarce (Chrome):")
        print(f"\n{auth_url}\n")
        print("KROK 2: Po zalogowaniu i kliknięciu 'Potwierdź', przeglądarka wyświetli błąd")
        print("       (np. Ta witryna jest nieosiągalna).")
        print("KROK 3: SKOPIUJ z paska adresu przeglądarki wartość po 'code='.")
        print("       Przykład: Jeśli adres to http://localhost:8000/?code=XYZ123..., skopiuj XYZ123...")
        print("="*80 + "\n")
        
        code = input("Wklej tutaj skopiowany kod 'code' i naciśnij Enter: ").strip()
        if not code:
            logger.error("Brak kodu. Przerywam.")
            return False
            
        return self.exchange_code_for_token(code)

    def exchange_code_for_token(self, code):
        url = "https://allegro.pl/auth/oauth/token"
        data = {"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI}
        resp = requests.post(url, auth=(self.client_id, self.client_secret), data=data)
        if resp.status_code == 200:
            tokens = resp.json()
            self.save_tokens(tokens)
            logger.info("Autoryzacja pomyślna!")
            return True
        else:
            logger.error(f"Błąd wymiany kodu: {resp.text}")
            return False

    def refresh_access_token(self):
        url = "https://allegro.pl/auth/oauth/token"
        data = {"grant_type": "refresh_token", "refresh_token": self.refresh_token, "redirect_uri": REDIRECT_URI}
        resp = requests.post(url, auth=(self.client_id, self.client_secret), data=data)
        if resp.status_code == 200:
            tokens = resp.json()
            self.save_tokens(tokens)
            return True
        return False

    def save_tokens(self, tokens):
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]
        with open(TOKEN_FILE, "w") as f:
            json.dump(tokens, f)

    def load_tokens(self):
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r") as f:
                    tokens = json.load(f)
                    self.access_token = tokens["access_token"]
                    self.refresh_token = tokens["refresh_token"]
                    return True
            except: pass
        return False

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.allegro.public.v1+json"
        }

    def find_cheapest_by_ean(self, ean):
        if not ean or ean == "BRAK" or len(str(ean)) < 8: return None
        url = "https://api.allegro.pl/offers/listing"
        params = {"phrase": ean, "limit": 5, "sort": "+price", "fallback": "false"}
        try:
            resp = requests.get(url, headers=self.get_headers(), params=params)
            if resp.status_code == 401:
                if self.refresh_access_token():
                    resp = requests.get(url, headers=self.get_headers(), params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", {})
            offers = items.get("regular", [])
            if not offers: offers = items.get("promoted", [])
            if not offers: return None
            best = offers[0]
            return {
                "price": float(best["sellingMode"]["price"]["amount"]),
                "name": best["name"],
                "url": f"https://allegro.pl/oferta/{best['id']}"
            }
        except Exception as e:
            logger.debug(f"EAN {ean} error: {e}")
            return None

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", help="Allegro authorization code")
    args = parser.parse_args()

    # 1. Znajdź plik eksportu (najnowszy final lub potential)
    import glob
    files = glob.glob("gapli_final_prices_final_*.xlsx") + glob.glob("gapli_potential_products_*.xlsx")
    if not files:
        logger.error("Brak pliku eksportu Gapli!")
        return
    input_file = sorted(files)[-1]
    logger.info(f"Wczytywanie danych z: {input_file}")
    df = pd.read_excel(input_file)

    # 2. Inicjalizacja Allegro API
    if not CLIENT_ID or not CLIENT_SECRET:
        logger.error("Brak kluczy Allegro!")
        return
        
    api = AllegroAPI(CLIENT_ID, CLIENT_SECRET)
    if args.code:
        if not api.exchange_code_for_token(args.code):
            return
    elif not api.load_tokens():
        if not api.manual_auth(): return
    else:
        try: 
            if not api.refresh_access_token():
                if not api.manual_auth(): return
        except:
            if not api.manual_auth(): return

    results = []
    # Wykrywanie kolumny z ceną
    price_col = 'Cena w Gapli' if 'Cena w Gapli' in df.columns else 'Cena Brutto (Gapli)'
    if price_col not in df.columns:
        logger.error(f"Nie znaleziono kolumny z ceną! Dostępne: {df.columns.tolist()}")
        return

    # 3. Procesowanie produktów
    logger.info(f"Rozpoczynanie sprawdzania {len(df)} produktów...")
    for index, row in df.iterrows():
        sku = row['SKU']
        ean = str(row['EAN']).strip()
        my_price = float(row[price_col])
        
        logger.info(f"[{index+1}/{len(df)}] Sprawdzanie {sku} (EAN: {ean})")
        comp = api.find_cheapest_by_ean(ean)
        
        if comp:
            diff = round(my_price - comp['price'], 2)
            results.append({
                "SKU": sku,
                "EAN": ean,
                "Nazwa": row['Nazwa Produktu'],
                "Moja Cena (Gapli)": my_price,
                "Najtańszy Allegro": comp['price'],
                "Różnica": diff,
                "Status": "DROŻSZY" if diff > 0 else "OK",
                "Link": comp['url']
            })
            logger.info(f"   -> Wynik: {comp['price']} (Różnica: {diff})")
        else:
            results.append({
                "SKU": sku,
                "EAN": ean,
                "Nazwa": row['Nazwa Produktu'],
                "Moja Cena (Gapli)": my_price,
                "Najtańszy Allegro": "Brak ofert",
                "Różnica": "",
                "Status": "Brak konkurencji",
                "Link": ""
            })
            logger.info(f"   -> Brak ofert konkurencji.")
            
        time.sleep(0.4) # Politeness

    # 4. Zapisz raport
    output_df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"raport_cen_konkurencji_{timestamp}.xlsx"
    output_df.to_excel(output_file, index=False)
    logger.info(f"RAPORT GOTOWY: {output_file}")

if __name__ == "__main__":
    main()

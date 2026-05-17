import os
import json
import logging
import time
import requests
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- KONFIGURACJA ---
# Dane pobierane ze zmiennych środowiskowych (Ustaw je wcześniej!)
# setx ALLEGRO_CLIENT_ID "twoj_id"
# setx ALLEGRO_CLIENT_SECRET "twoj_secret"
CLIENT_ID = os.environ.get("skarbiec_client_id")
CLIENT_SECRET = os.environ.get("skarbiec_client_secret")
REDIRECT_URI = "http://localhost:8000"
TOKEN_FILE = "allegro_token.json"

class AllegroAuthHandler(BaseHTTPRequestHandler):
    """Prosty serwer do odebrania kodu autoryzacji z Allegro."""
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        if "code" in params:
            self.server.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("Autoryzacja pomyślna! Możesz zamknąć to okno i wrócić do konsoli.".encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()

class AllegroAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None

    def get_auth_code(self):
        """Otwiera przeglądarkę w celu uzyskania zgody użytkownika."""
        auth_url = f"https://allegro.pl/auth/oauth/authorize?response_type=code&client_id={self.client_id}&redirect_uri={REDIRECT_URI}"
        logger.info(f"Otwieranie przeglądarki w celu autoryzacji: {auth_url}")
        webbrowser.open(auth_url)
        
        server = HTTPServer(("localhost", 8000), AllegroAuthHandler)
        server.auth_code = None
        logger.info("Oczekiwanie na kod autoryzacji na porcie 8000...")
        server.handle_request()
        return server.auth_code

    def exchange_code_for_token(self, code):
        """Wymienia kod na token dostępu."""
        url = "https://allegro.pl/auth/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
        response = requests.post(url, auth=(self.client_id, self.client_secret), data=data)
        response.raise_for_status()
        tokens = response.json()
        self.save_tokens(tokens)
        return tokens

    def refresh_access_token(self):
        """Odświeża token dostępu."""
        url = "https://allegro.pl/auth/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "redirect_uri": REDIRECT_URI
        }
        response = requests.post(url, auth=(self.client_id, self.client_secret), data=data)
        response.raise_for_status()
        tokens = response.json()
        self.save_tokens(tokens)
        return tokens

    def save_tokens(self, tokens):
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]
        with open(TOKEN_FILE, "w") as f:
            json.dump(tokens, f)

    def load_tokens(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                tokens = json.load(f)
                self.access_token = tokens["access_token"]
                self.refresh_token = tokens["refresh_token"]
                return True
        return False

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.allegro.public.v1+json"
        }

    def find_cheapest_by_ean(self, ean):
        """Wyszukuje najtańszą ofertę dla danego EAN (z wyłączeniem własnych, jeśli to możliwe)."""
        if not ean: return None

        url = "https://api.allegro.pl/offers/listing"
        params = {
            "phrase": ean,
            "limit": 10,
            "sort": "+price" # Sortowanie od najniższej ceny
        }

        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            if response.status_code == 401:
                self.refresh_access_token()
                response = requests.get(url, headers=self.get_headers(), params=params)

            response.raise_for_status()
            data = response.json()

            # Pobieramy oferty z sekcji 'regular' (pomiń promowane jeśli chcesz tylko najniższą bazową)
            offers = data.get("items", {}).get("regular", [])
            if not offers:
                return None

            cheapest = offers[0]
            return {
                "price": float(cheapest["sellingMode"]["price"]["amount"]),
                "currency": cheapest["sellingMode"]["price"]["currency"],
                "name": cheapest["name"],
                "vendor": cheapest.get("seller", {}).get("id", "N/A")
            }
        except Exception as e:
            logger.error(f"Błąd podczas sprawdzania EAN {ean}: {e}")
            return None

    def get_ean_from_offer(self, offer_id):
        """Pobiera EAN (GTIN) bezpośrednio z oferty na Allegro."""
        if not offer_id: return None
        url = f"https://api.allegro.pl/sale/offers/{offer_id}"
        try:
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 401:
                self.refresh_access_token()
                response = requests.get(url, headers=self.get_headers())

            response.raise_for_status()
            data = response.json()

            # EAN/GTIN jest zazwyczaj w sekcji product
            ean = data.get("product", {}).get("gtin")

            # Jeśli nie ma w sekcji product, sprawdź parametry
            if not ean:
                parameters = data.get("parameters", [])
                for param in parameters:
                    if param.get("id") == "225693": # ID parametru EAN/GTIN na Allegro
                        values = param.get("values", [])
                        if values:
                            ean = values[0]
                            break

            return ean
        except Exception as e:
            logger.debug(f"Nie udało się pobrać EAN dla oferty {offer_id}: {e}")
            return None

def extract_ean_from_name(name):
    """Próbuje wyciągnąć EAN (13 cyfr) z nazwy produktu."""
    import re
    # Szukamy 13 cyfr, często zaczynających się od 590 (Polska) lub po prostu 13 cyfrowych ciągów
    match = re.search(r'\b(\d{13})\b', name)
    if match:
        return match.group(1)
    return None

def load_sku_ean_mapping(file_path):
    """Wczytuje mapowanie SKU -> EAN z pliku produktów Gapli."""
    mapping = {}
    if not os.path.exists(file_path):
        logger.warning(f"Plik {file_path} nie istnieje. Nie można wczytać mapowania SKU-EAN.")
        return mapping

    try:
        logger.info(f"Wczytywanie mapowania SKU-EAN z {file_path}...")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                sku = item.get("sku")
                ean = item.get("ean")
                if sku and ean:
                    mapping[sku] = ean
        logger.info(f"Wczytano {len(mapping)} mapowań SKU-EAN.")
    except Exception as e:
        logger.error(f"Błąd podczas wczytywania mapowania: {e}")
    return mapping

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("\nBŁĄD: Brak kluczy API Allegro!")
        print("Ustaw je w systemie Windows:")
        print('setx skarbiec_client_id "twoj_client_id"')
        print('setx skarbiec_client_secret "twoj_secret"')
        return

    api = AllegroAPI(CLIENT_ID, CLIENT_SECRET)

    # 1. Autoryzacja
    if not api.load_tokens():
        code = api.get_auth_code()
        api.exchange_code_for_token(code)
    else:
        try:
            api.refresh_access_token()
        except:
            code = api.get_auth_code()
            api.exchange_code_for_token(code)

    # 2. Wczytaj mapowanie EAN z bazy Gapli
    sku_ean_map = load_sku_ean_mapping("gapli_products_list.json")

    # 3. Wczytaj produkty z Marketplace (Allegro)
    marketplace_file = "allegro_marketplace_products.json"
    if not os.path.exists(marketplace_file):
        logger.error(f"Brak pliku {marketplace_file}. Uruchom najpierw fetch_allegro_products.py")
        return

    with open(marketplace_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []

    # Iterujemy po kontach i produktach
    for account_key, account_data in data.items():
        products = account_data.get("products", [])
        logger.info(f"Przetwarzanie {len(products)} produktów dla konta {account_key}...")

        for prod in products:
            sku = prod.get("sku")
            name = prod.get("name")
            my_price = float(prod.get("price", 0))
            offer_id = prod.get("allegro_offer_id")

            # Próba uzyskania EAN - najpierw z mapowania SKU (najpewniejsze)
            ean = sku_ean_map.get(sku)

            if not ean:
                # Jeśli nie ma w mapowaniu, sprawdź czy jest już w danych produktu
                ean = prod.get("ean") 

            if not ean:
                # 1. Próba z nazwy
                ean = extract_ean_from_name(name)
                if ean:
                    logger.info(f"Znaleziono EAN w nazwie: {ean}")

            if not ean and offer_id:
                # 2. Próba z Allegro API (najwolniejsza metoda)
                logger.info(f"Pobieranie EAN z Allegro dla oferty {offer_id}...")
                ean = api.get_ean_from_offer(offer_id)
                if ean:
                    logger.info(f"Pobrano EAN z Allegro: {ean}")

            if not ean:
                logger.warning(f"Produkt {sku} ({name}) nie ma EAN. Pomijam.")
                continue

            logger.info(f"Sprawdzanie konkurencji dla: {name} (EAN: {ean})")
            comp = api.find_cheapest_by_ean(ean)
            if comp:
                diff = my_price - comp["price"]
                results.append({
                    "Konto": account_key,
                    "SKU": sku,
                    "Nazwa": name,
                    "EAN": ean,
                    "Moja Cena": my_price,
                    "Najtańsza Konkurencja": comp["price"],
                    "Różnica": round(diff, 2),
                    "Status": "DROŻSZY" if diff > 0 else "TAŃSZY/OK",
                    "Link Konkurencji": f"https://allegro.pl/listing?string={ean}"
                })
                logger.info(f"Wynik: Moja: {my_price} | Konkurencja: {comp['price']} | Różnica: {round(diff, 2)}")
            else:
                logger.info("Nie znaleziono ofert konkurencji.")
            
            # Przerwa aby nie przeciążyć API Allegro
            time.sleep(0.5)

    # 4. Zapis do CSV (łatwy do otwarcia w Excel)
    import csv
    output_file = "raport_cen_allegro.csv"
    if results:
        keys = results[0].keys()
        with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys, delimiter=";")
            dict_writer.writeheader()
            dict_writer.writerows(results)
        logger.info(f"Raport zapisany do: {output_file}")
    else:
        logger.warning("Nie zebrano żadnych danych do raportu.")

if __name__ == "__main__":
    main()

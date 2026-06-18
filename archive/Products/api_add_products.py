import os
import requests
import json
import logging
import time
from datetime import datetime
import openpyxl

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- KONFIGURACJA ---
STORES = ["hit_bazar", "radosnydzieciak", "skarbiec_ofert"]
WHOLESALERS_FILE = "Recorded/hurtownie_allegro.xlsx"

CONFIG = {
    'min_price': 60,
    'max_price': 50000,
    'min_stock': 2
}

class GapliAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://gapli.com/api/v1/integrations"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_accounts(self):
        """Pobiera listę kont marketplace."""
        url = f"{self.base_url}/marketplace/accounts"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("accounts", [])

    def get_wholesalers(self):
        """Pobiera listę hurtowni (parserów)."""
        url = f"https://gapli.com/api/v1/integrations/wholesalers"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("wholesalers", [])

    def get_products(self, parser_id, min_price, max_price, min_stock):
        """Pobiera produkty z danej hurtowni spełniające kryteria."""
        url = f"{self.base_url}/products"
        all_products = []
        offset = 0
        limit = 200

        params = {
            "parser_id": parser_id,
            "price_gross_min": min_price,
            "price_gross_max": max_price,
            "stock_min": min_stock,
            "available": "true",
            "limit": limit
        }

        while True:
            params["offset"] = offset
            logger.info(f"Pobieranie produktów (parser_id: {parser_id}, offset: {offset})...")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            products = data.get("products", [])
            if not products:
                break
                
            all_products.extend(products)
            
            if not data.get("pagination", {}).get("has_more", False):
                break
                
            offset += len(products)
            time.sleep(0.1) # Mała przerwa dla API

        return all_products

    def send_to_marketplace(self, account_id, skus, min_price, max_price):
        """Wysyła produkty na konto Allegro."""
        url = f"{self.base_url}/marketplace/listing"
        
        # Batching SKUs (max 100 na raz dla bezpieczeństwa)
        batch_size = 100
        for i in range(0, len(skus), batch_size):
            batch = skus[i:i + batch_size]
            body = {
                "action": "send",
                "account_id": account_id,
                "product_skus": batch,
                "price_range": {
                    "min": min_price,
                    "max": max_price
                }
            }
            
            logger.info(f"Wysyłanie partii {len(batch)} produktów na konto {account_id}...")
            response = requests.post(url, headers=self.headers, json=body)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 30))
                logger.warning(f"Rate limit! Czekam {retry_after}s...")
                time.sleep(retry_after)
                # Ponów tę partię
                i -= batch_size 
                continue

            response.raise_for_status()
            logger.info(f"Odpowiedź API: {response.json().get('message', 'Sukces')}")
            time.sleep(0.5)

def read_wholesalers_from_excel(file_path):
    """Wczytuje nazwy hurtowni z pliku Excel."""
    if not os.path.exists(file_path):
        logger.error(f"Plik {file_path} nie istnieje!")
        return []
    
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    return [row[0] for row in ws.iter_rows(min_row=2, values_only=True) if row[0]]

def main():
    api_key = os.environ.get("Gapli_Apikey")
    if not api_key:
        logger.error("Błąd: Brak zmiennej 'Gapli_Apikey'.")
        return

    client = GapliAPIClient(api_key)

    # 1. Pobierz mapowanie kont
    logger.info("Pobieranie kont Allegro...")
    accounts = client.get_accounts()
    store_to_account_id = {acc['store_name']: acc['id'] for acc in accounts if acc.get('platform') == 'allegro'}
    
    # 2. Pobierz mapowanie hurtowni
    logger.info("Pobieranie listy hurtowni z API...")
    api_wholesalers = client.get_wholesalers()
    wholesaler_name_to_id = {w['name']: w['parser_id'] for w in api_wholesalers if w.get('parser_id')}

    # 3. Wczytaj hurtownie do przetworzenia
    target_wholesalers = read_wholesalers_from_excel(WHOLESALERS_FILE)
    
    if not target_wholesalers:
        logger.warning("Brak hurtowni do przetworzenia.")
        return

    for store_name in STORES:
        account_id = store_to_account_id.get(store_name)
        if not account_id:
            logger.warning(f"Nie znaleziono konta Allegro dla sklepu: {store_name}")
            continue
            
        logger.info(f"=== ROZPOCZYNANIE PRACY DLA SKLEPU: {store_name} (ID: {account_id}) ===")
        
        for w_name in target_wholesalers:
            parser_id = wholesaler_name_to_id.get(w_name)
            if not parser_id:
                logger.warning(f"Hurtownia '{w_name}' nie została znaleziona w API (brak parser_id).")
                continue
                
            logger.info(f"Przetwarzanie hurtowni: {w_name} (parser_id: {parser_id})")
            
            try:
                # Pobierz produkty spełniające kryteria
                products = client.get_products(
                    parser_id, 
                    CONFIG['min_price'], 
                    CONFIG['max_price'], 
                    CONFIG['min_stock']
                )
                
                if not products:
                    logger.info(f"Brak produktów spełniających kryteria dla {w_name}.")
                    continue
                
                skus = [p['sku'] for p in products if p.get('sku')]
                logger.info(f"Znaleziono {len(skus)} produktów gotowych do wysłania.")
                
                # Wyślij na Allegro
                client.send_to_marketplace(
                    account_id, 
                    skus, 
                    CONFIG['min_price'], 
                    CONFIG['max_price']
                )
                
            except Exception as e:
                logger.error(f"Błąd podczas przetwarzania {w_name} dla {store_name}: {e}")

    logger.info("Zakończono przetwarzanie wszystkich sklepów.")

if __name__ == "__main__":
    main()

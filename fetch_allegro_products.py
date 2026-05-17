import os
import requests
import json
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_allegro_accounts(api_key):
    """Pobiera listę kont marketplace i zwraca ID kont Allegro."""
    url = "https://gapli.com/api/v1/integrations/marketplace/accounts"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            logger.error("Błąd podczas pobierania kont marketplace.")
            return []
            
        accounts = data.get("accounts", [])
        allegro_accounts = [acc for acc in accounts if acc.get("platform") == "allegro"]
        
        for acc in allegro_accounts:
            logger.info(f"Znaleziono konto Allegro: ID={acc['id']}, Nazwa='{acc['name']}'")
            
        return allegro_accounts
    except Exception as e:
        logger.error(f"Wystąpił błąd podczas pobierania kont: {e}")
        return []

def fetch_marketplace_products(api_key, account_id):
    """Pobiera wszystkie produkty dla danego konta marketplace z obsługą błędów i ponowień."""
    endpoint = "https://gapli.com/api/v1/integrations/marketplace/products"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    
    all_products = []
    offset = 0
    limit = 50 
    max_retries = 5
    
    logger.info(f"Pobieranie produktów dla konta ID: {account_id}...")
    
    import time
    
    while True:
        retries = 0
        success = False
        
        while retries < max_retries and not success:
            try:
                params = {
                    "account_id": account_id,
                    "limit": limit,
                    "offset": offset
                }
                
                response = requests.get(endpoint, headers=headers, params=params, timeout=40)
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 10))
                    logger.warning(f"Rate limit! Czekam {retry_after}s...")
                    time.sleep(retry_after)
                    continue # Nie zwiększaj retries dla 429
                
                if response.status_code in [500, 502, 503, 504]:
                    retries += 1
                    wait_time = retries * 5 # Progresywny czas oczekiwania
                    logger.warning(f"Błąd serwera {response.status_code}. Ponowienie {retries}/{max_retries} za {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                data = response.json()
                
                if not data.get("success"):
                    logger.error(f"API zwróciło success=false: {data.get('message')}")
                    return all_products # Zwróć to co udało się pobrać
                    
                current_batch = data.get("products", [])
                if not current_batch:
                    return all_products # Koniec danych
                    
                all_products.extend(current_batch)
                logger.info(f"Pobrano {len(current_batch)} produktów. Łącznie: {len(all_products)}")
                
                pagination = data.get("pagination", {})
                if not pagination.get("has_more", False):
                    return all_products
                    
                offset += len(current_batch)
                success = True
                # Mała przerwa między zapytaniami dla stabilności
                time.sleep(0.2)
                
            except Exception as e:
                retries += 1
                wait_time = retries * 5
                logger.error(f"Błąd sieciowy: {e}. Ponowienie {retries}/{max_retries} za {wait_time}s...")
                time.sleep(wait_time)
        
        if not success:
            logger.error(f"Nie udało się pobrać kolejnej partii danych dla konta {account_id} po {max_retries} próbach.")
            break
            
    return all_products

def main():
    api_key = os.environ.get("Gapli_Apikey")
    if not api_key:
        logger.error("Błąd: Brak zmiennej środowiskowej 'Gapli_Apikey'.")
        return

    # 1. Pobierz konta
    logger.info("Sprawdzanie kont Allegro...")
    allegro_accounts = get_allegro_accounts(api_key)
    
    if not allegro_accounts:
        logger.warning("Nie znaleziono żadnych aktywnych kont Allegro.")
        return

    all_allegro_data = {}

    # 2. Pobierz produkty dla każdego konta Allegro
    for acc in allegro_accounts:
        acc_id = acc["id"]
        acc_name = acc["name"]
        
        # Używamy kombinacji Nazwa + ID jako klucza, aby uniknąć nadpisywania kont o tej samej nazwie
        unique_key = f"{acc_name} (ID: {acc_id})"
        
        products = fetch_marketplace_products(api_key, acc_id)
        all_allegro_data[unique_key] = {
            "account_info": acc,
            "products": products,
            "total_fetched": len(products)
        }

    # 3. Zapisz wyniki
    filename = "allegro_marketplace_products.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_allegro_data, f, indent=4, ensure_ascii=False)
    
    logger.info(f"Zakończono. Łącznie przetworzono {len(all_allegro_data)} kont.")
    logger.info(f"Dane zapisane do pliku: {filename}")

if __name__ == "__main__":
    main()

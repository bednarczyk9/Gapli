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

def fetch_gapli_products():
    """
    Pobiera listę wszystkich produktów z API Gapli (integrations).
    Klucz API musi być zapisany w zmiennej środowiskowej Gapli_Apikey.
    """
    # Pobranie klucza API z zmiennych środowiskowych Windows
    api_key = os.environ.get("Gapli_Apikey")
    
    if not api_key:
        logger.error("Błąd: Zmienna środowiskowa 'Gapli_Apikey' nie jest ustawiona.")
        print("\nINSTRUKCJA: Ustaw klucz API w konsoli przed uruchomieniem:")
        print("setx Gapli_Apikey \"twoj_klucz_api\"")
        print("Następnie zrestartuj terminal.")
        return None

    # Dokumentacja: Base URL i endpointy
    base_url = "https://gapli.com/api/v1"
    endpoint = f"{base_url}/integrations/products"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    all_products = []
    offset = 0
    limit = 200 # Maksymalny limit wg dokumentacji
    
    logger.info("Rozpoczynam pobieranie produktów z katalogów hurtowni (Gapli Integrations API)...")

    while True:
        try:
            params = {
                "offset": offset,
                "limit": limit,
                "available": "true" # Opcjonalnie: pobieraj tylko dostępne produkty
            }
            
            logger.info(f"Pobieranie produktów (offset: {offset}, limit: {limit})...")
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            
            # Obsługa błędów autoryzacji
            if response.status_code == 401:
                logger.error("Błąd 401: Nieautoryzowany dostęp. Sprawdź czy klucz Gapli_Apikey jest poprawny i zaczyna się od 'gapli_'.")
                break
            
            # Obsługa Rate Limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                logger.warning(f"Przekroczono limit zapytań (Rate Limit). Czekam {retry_after} sekund...")
                import time
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            data = response.json()
            
            if not data.get("success"):
                logger.error(f"API zwróciło błąd sukcesu: {data.get('message', 'Nieznany błąd')}")
                break

            current_batch = data.get("products", [])
            
            if not current_batch:
                logger.info("Brak więcej produktów do pobrania.")
                break
            
            all_products.extend(current_batch)
            logger.info(f"Pobrano {len(current_batch)} produktów. Łącznie: {len(all_products)}")
            
            # Sprawdzenie paginacji na podstawie dokumentacji
            pagination = data.get("pagination", {})
            has_more = pagination.get("has_more", False)
            
            if not has_more:
                logger.info("Osiągnięto koniec listy (has_more: false).")
                break
            
            # Zwiększenie offsetu o liczbę pobranych produktów lub limit
            offset += len(current_batch)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Wystąpił błąd sieciowy: {e}")
            break
        except Exception as e:
            logger.error(f"Wystąpił nieoczekiwany błąd: {e}")
            break

    return all_products

def save_products_to_file(products, filename="gapli_products_list.json"):
    """Zapisuje listę produktów do pliku JSON."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=4, ensure_ascii=False)
        logger.info(f"Pomyślnie zapisano {len(products)} produktów do pliku: {filename}")
        return True
    except Exception as e:
        logger.error(f"Błąd podczas zapisywania pliku: {e}")
        return False

if __name__ == "__main__":
    products = fetch_gapli_products()
    
    if products:
        print(f"\n--- WYNIK ---")
        print(f"Pobrano łącznie: {len(products)} produktów.")
        
        # Zapis do pliku
        save_products_to_file(products)
        
        # Przykładowe wyświetlenie pierwszych 3 produktów (jeśli istnieją)
        if len(products) > 0:
            print("\nPodgląd pierwszych produktów:")
            for p in products[:3]:
                # Próba wyświetlenia nazwy/tytułu (zależnie od schematu API)
                name = p.get("name") or p.get("title") or p.get("product_name") or "Brak nazwy"
                price = p.get("price") or p.get("sale_price") or "N/A"
                print(f"- {name} (Cena: {price})")
    else:
        print("\nNie udało się pobrać listy produktów. Sprawdź logi powyżej.")

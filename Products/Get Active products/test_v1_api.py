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

def test_v1_api():
    api_key = os.environ.get("Gapli_Apikey")
    if not api_key:
        logger.error("Brak Gapli_Apikey w środowisku.")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    # 1. Pobierz konta marketplace
    logger.info("Pobieranie kont marketplace...")
    try:
        resp = requests.get("https://gapli.com/api/v1/integrations/marketplace/accounts", headers=headers)
        resp.raise_for_status()
        accounts_data = resp.json()
        with open("api_v1_accounts.json", "w", encoding="utf-8") as f:
            json.dump(accounts_data, f, indent=4, ensure_ascii=False)
        
        accounts = accounts_data.get("accounts", [])
        allegro_accounts = [a for a in accounts if a.get("platform") == "allegro"]
        
        if not allegro_accounts:
            logger.warning("Nie znaleziono kont Allegro.")
            return

        acc = allegro_accounts[0]
        logger.info(f"Testowanie dla konta: {acc['name']} (ID: {acc['id']})")

        # 2. Pobierz produkty dla pierwszego konta
        params = {
            "account_id": acc["id"],
            "limit": 1
        }
        logger.info(f"Pobieranie produktów dla konta {acc['id']}...")
        resp = requests.get("https://gapli.com/api/v1/integrations/marketplace/products", headers=headers, params=params)
        resp.raise_for_status()
        products_data = resp.json()
        
        with open("api_v1_products_sample.json", "w", encoding="utf-8") as f:
            json.dump(products_data, f, indent=4, ensure_ascii=False)
            
        logger.info("Próbka danych zapisana do api_v1_products_sample.json")
        
        if products_data.get("products"):
            first_product = products_data["products"][0]
            logger.info(f"Klucze produktu: {list(first_product.keys())}")
            # Sprawdź czy są opisy i parametry
            logger.info(f"Czy jest opis? {'description' in first_product}")
            logger.info(f"Czy są parametry? {'parameters' in first_product or 'attributes' in first_product}")

    except Exception as e:
        logger.error(f"Błąd API V1: {e}")

if __name__ == "__main__":
    test_v1_api()

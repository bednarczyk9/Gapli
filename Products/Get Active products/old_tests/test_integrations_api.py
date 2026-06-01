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

def test_integrations_api():
    api_key = os.environ.get("Gapli_Apikey")
    if not api_key:
        logger.error("Brak Gapli_Apikey.")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    # Pobierz 1 produkt z katalogu hurtowni
    params = {
        "limit": 1
    }
    
    logger.info("Pobieranie produktu z Gapli Integrations API...")
    resp = requests.get("https://gapli.com/api/v1/integrations/products", headers=headers, params=params)
    if resp.status_code == 200:
        data = resp.json()
        with open("integrations_product_sample.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        if data.get("products"):
            p = data["products"][0]
            logger.info(f"Klucze: {list(p.keys())}")
            logger.info(f"Opis obecny: {'description' in p}")
            logger.info(f"Parametry obecne: {'parameters' in p or 'attributes' in p}")
    else:
        logger.warning(f"Błąd: {resp.status_code}")

if __name__ == "__main__":
    test_integrations_api()

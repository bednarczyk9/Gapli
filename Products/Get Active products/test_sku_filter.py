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

def test_sku_filter():
    api_key = os.environ.get("Gapli_Apikey")
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    
    # Próbujemy filtrować po jednym SKU
    sku = "18277_2"
    params = {"sku": sku}
    resp = requests.get("https://gapli.com/api/v1/integrations/products", headers=headers, params=params)
    if resp.status_code == 200:
        data = resp.json()
        logger.info(f"Filtrowanie po sku={sku}: Znaleziono {len(data.get('products', []))} produktów.")
    else:
        logger.warning(f"Błąd filtrowania po sku: {resp.status_code}")

    # Próbujemy filtrować po wielu SKU (jeśli API to wspiera)
    skus = "18277_2,11326_2"
    params = {"skus": skus}
    resp = requests.get("https://gapli.com/api/v1/integrations/products", headers=headers, params=params)
    if resp.status_code == 200:
        data = resp.json()
        logger.info(f"Filtrowanie po skus={skus}: Znaleziono {len(data.get('products', []))} produktów.")
    else:
        logger.warning(f"Błąd filtrowania po skus: {resp.status_code}")

if __name__ == "__main__":
    test_sku_filter()

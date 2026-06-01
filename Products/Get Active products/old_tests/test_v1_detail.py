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

def test_v1_detail():
    api_key = os.environ.get("Gapli_Apikey")
    if not api_key:
        logger.error("Brak Gapli_Apikey.")
        return

    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    
    # Przykładowe ID konta i produktu (z poprzedniego testu)
    account_id = 116
    
    # Najpierw pobierz ID produktu
    resp = requests.get(f"https://gapli.com/api/v1/integrations/marketplace/products?account_id={account_id}&limit=1", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("products"):
            p = data["products"][0]
            p_id = p["id"]
            logger.info(f"Testowanie szczegółów V1 dla produktu ID: {p_id}")
            
            detail_url = f"https://gapli.com/api/v1/integrations/marketplace/products/{p_id}"
            resp_detail = requests.get(detail_url, headers=headers)
            if resp_detail.status_code == 200:
                detail = resp_detail.json()
                with open("v1_product_detail.json", "w", encoding="utf-8") as f:
                    json.dump(detail, f, indent=4, ensure_ascii=False)
                logger.info("Sukces! Dane V1 zapisane.")
                
                prod = detail.get("product", {})
                logger.info(f"Opis obecny: {'description' in prod}")
                logger.info(f"Parametry obecne: {'parameters' in prod or 'attributes' in prod}")
            else:
                logger.warning(f"Szczegóły V1 zwróciły {resp_detail.status_code}")
        else:
            logger.warning("Brak produktów na koncie.")
    else:
        logger.warning(f"Błąd przy pobieraniu listy V1: {resp.status_code}")

if __name__ == "__main__":
    test_v1_detail()

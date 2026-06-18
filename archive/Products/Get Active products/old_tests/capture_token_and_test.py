import os
import time
import json
import logging
import requests
from playwright.sync_api import sync_playwright
from keywords.gapli_keywords import start_browser_and_login

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def capture_token_and_test():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")

    if not username or not password:
        logger.error("Błąd: Zmienne środowiskowe GAPLI_USER lub GAPLI_PASS nie są ustawione.")
        return

    logger.info("Uruchamianie przeglądarki i logowanie do Gapli...")
    playwright_instance, page, client = start_browser_and_login(username, password)

    if not page:
        logger.error("Nie udało się zalogować.")
        if playwright_instance:
            playwright_instance.stop()
        return

    auth_token = None

    def handle_request(request):
        nonlocal auth_token
        url = request.url
        if "/api/" in url and "Authorization" in request.headers:
            auth_token = request.headers["Authorization"]
            # logger.info(f"Przechwycono token z {url}")

    page.on("request", handle_request)

    try:
        logger.info("Nawigacja do marketplace...")
        page.goto("https://gapli.com/dashboard/marketplace", wait_until="networkidle", timeout=60000)
        time.sleep(5)

        if not auth_token:
            logger.error("Nie udało się przechwycić tokenu autoryzacji.")
            return

        logger.info(f"Przechwycono token: {auth_token[:20]}...")

        # Testuj endpoint internal API z mode=full
        headers = {
            "Authorization": auth_token,
            "Accept": "application/json"
        }

        # Spróbujmy pobrać listę produktów z mode=full (o ile taki istnieje)
        test_url = "https://gapli.com/api/products-manager/products?page=1&limit=1&mode=full"
        logger.info(f"Testowanie internal API: {test_url}")
        
        resp = requests.get(test_url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            with open("internal_api_full_sample.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info("Sukces! Zapisano próbkę z mode=full do internal_api_full_sample.json")
            
            if data.get("products"):
                p = data["products"][0]
                logger.info(f"Klucze: {list(p.keys())}")
                logger.info(f"Opis obecny: {'description' in p or 'desc' in p}")
        else:
            logger.warning(f"mode=full zwrócił status {resp.status_code}")

        # Spróbujmy pobrać pojedynczy produkt (jeśli mamy ID z lean)
        lean_url = "https://gapli.com/api/products-manager/products?page=1&limit=1&mode=lean"
        resp_lean = requests.get(lean_url, headers=headers)
        if resp_lean.status_code == 200:
            lean_data = resp_lean.json()
            if lean_data.get("products"):
                p_lean = lean_data["products"][0]
                product_id = p_lean.get("id")
                sku = p_lean.get("sku")
                parser_id = p_lean.get("parser_id")
                
                logger.info(f"Próba pobrania szczegółów dla ID: {product_id}, SKU: {sku}, Parser: {parser_id}")
                
                # Różne warianty endpointu szczegółów
                variants = [
                    f"https://gapli.com/api/products-manager/products/{product_id}",
                    f"https://gapli.com/api/products-manager/products/{sku}_{parser_id}",
                    f"https://gapli.com/api/products-manager/wholesalers/products/{sku}_{parser_id}"
                ]
                
                for v_url in variants:
                    logger.info(f"Testowanie variantu: {v_url}")
                    r = requests.get(v_url, headers=headers)
                    if r.status_code == 200:
                        logger.info(f"Sukces na {v_url}!")
                        detail_data = r.json()
                        with open(f"internal_api_detail_{variants.index(v_url)}.json", "w", encoding="utf-8") as f:
                            json.dump(detail_data, f, indent=4, ensure_ascii=False)
                        break
                    else:
                        logger.warning(f"Status {r.status_code} dla {v_url}")

    except Exception as e:
        logger.error(f"Błąd: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    capture_token_and_test()

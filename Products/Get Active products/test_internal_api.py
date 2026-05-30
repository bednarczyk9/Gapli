import os
import time
import json
import logging
from playwright.sync_api import sync_playwright
from keywords.gapli_keywords import start_browser_and_login

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_internal_api_with_playwright():
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

    try:
        logger.info("Nawigacja do marketplace w celu zainicjowania sesji...")
        page.goto("https://gapli.com/dashboard/marketplace", wait_until="networkidle", timeout=60000)
        time.sleep(2)

        # Używamy page.request do robienia zapytań z sesją przeglądarki
        api_request_context = page.context.request

        # 1. Pobierz konta Allegro (internal API)
        logger.info("Pobieranie kont Allegro (internal API)...")
        resp = api_request_context.get("https://gapli.com/api/products-manager/allegro/accounts")
        if resp.status == 200:
            accounts = resp.json()
            with open("internal_accounts.json", "w", encoding="utf-8") as f:
                json.dump(accounts, f, indent=4, ensure_ascii=False)
            logger.info(f"Znaleziono {len(accounts.get('accounts', []))} kont.")
        else:
            logger.warning(f"Błąd przy pobieraniu kont: {resp.status}")

        # 2. Pobierz produkty (internal API)
        logger.info("Testowanie endpointu produktów z mode=full...")
        resp = api_request_context.get("https://gapli.com/api/products-manager/products?page=1&limit=5&mode=full")
        if resp.status == 200:
            data = resp.json()
            with open("internal_products_mode_full.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            if data.get("products"):
                p = data["products"][0]
                logger.info(f"Klucze (mode=full): {list(p.keys())}")
                logger.info(f"Opis obecny: {'description' in p or 'desc' in p}")
        else:
            logger.warning(f"mode=full zwrócił {resp.status}")

        # 3. Sprawdź szczegóły konkretnego produktu
        resp = api_request_context.get("https://gapli.com/api/products-manager/products?page=1&limit=1&mode=lean")
        if resp.status == 200:
            lean_data = resp.json()
            if lean_data.get("products"):
                p = lean_data["products"][0]
                sku = p.get("sku")
                parser_id = p.get("parser_id")
                
                logger.info(f"Pobieranie szczegółów dla: {sku}_{parser_id}...")
                
                detail_url = f"https://gapli.com/api/products-manager/products/{sku}_{parser_id}"
                resp_detail = api_request_context.get(detail_url)
                if resp_detail.status == 200:
                    detail_data = resp_detail.json()
                    with open("internal_product_detail.json", "w", encoding="utf-8") as f:
                        json.dump(detail_data, f, indent=4, ensure_ascii=False)
                    logger.info("Sukces! Szczegóły zapisane do internal_product_detail.json")
                    logger.info(f"Klucze szczegółów: {list(detail_data.get('product', {}).keys())}")
                    
                    # Sprawdź opis i parametry w szczegółach
                    prod_info = detail_data.get('product', {})
                    logger.info(f"Opis w szczegółach: {'description' in prod_info}")
                    logger.info(f"Parametry w szczegółach: {'parameters' in prod_info or 'attributes' in prod_info}")
                else:
                    logger.warning(f"Szczegóły zwróciły {resp_detail.status} dla {detail_url}")

    except Exception as e:
        logger.error(f"Błąd: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    test_internal_api_with_playwright()

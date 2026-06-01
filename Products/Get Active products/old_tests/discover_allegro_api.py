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

def discover_allegro_api():
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

    captured_requests = []

    def handle_response(response):
        url = response.url
        if "api/products-manager/allegro/products" in url:
            logger.info(f"Przechwycono odpowiedź z API: {url}")
            try:
                # Próbujemy pobrać fragment danych, aby zobaczyć strukturę
                data = response.json()
                captured_requests.append({
                    "url": url,
                    "sample_data": data
                })
            except Exception as e:
                logger.warning(f"Nie udało się odczytać JSON z {url}: {e}")

    page.on("response", handle_response)

    try:
        logger.info("Nawigacja do listy produktów Allegro...")
        # To jest URL z discovered_endpoints, może się różnić w UI
        page.goto("https://gapli.com/dashboard/products/allegro", wait_until="networkidle", timeout=60000)
        
        # Poczekaj chwilę na załadowanie danych
        time.sleep(10)
        
        # Spróbuj kliknąć w jakiś produkt, aby zobaczyć czy jest osobny endpoint na szczegóły (opisy, parametry)
        logger.info("Szukanie przycisku edycji/szczegółów produktu...")
        first_product_row = page.locator("table tbody tr").first
        if first_product_row.is_visible():
            logger.info("Klikam w pierwszy produkt, aby zobaczyć szczegóły...")
            first_product_row.click()
            time.sleep(5)

        if captured_requests:
            with open("allegro_api_structure.json", "w", encoding="utf-8") as f:
                json.dump(captured_requests, f, indent=4, ensure_ascii=False)
            logger.info("Zapisano strukturę API do allegro_api_structure.json")
        else:
            logger.warning("Nie przechwycono żadnych zapytań do API produktów Allegro.")

    except Exception as e:
        logger.error(f"Wystąpił błąd: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    discover_allegro_api()

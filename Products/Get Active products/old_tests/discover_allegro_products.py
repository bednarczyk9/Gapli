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

def discover_allegro_products_page():
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
        if "/api/" in url and "application/json" in response.headers.get("content-type", ""):
            try:
                data = response.json()
                captured_requests.append({
                    "url": url,
                    "data": data,
                    "headers": response.request.headers
                })
            except:
                pass

    page.on("response", handle_response)

    try:
        logger.info("Nawigacja do 'Twoje produkty Allegro'...")
        # Szukamy linku w sidebarze
        page.goto("https://gapli.com/dashboard", wait_until="networkidle")
        time.sleep(2)
        
        produkty_link = page.get_by_role("link", name="Produkty", exact=True)
        produkty_link.click()
        time.sleep(1)
        
        allegro_link = page.get_by_role("link", name="Twoje produkty Allegro")
        if not allegro_link.is_visible():
            allegro_link = page.locator("a:has-text('Twoje produkty Allegro')")
            
        if allegro_link.is_visible():
            allegro_link.click()
            logger.info("Kliknięto 'Twoje produkty Allegro'")
        else:
            logger.warning("Nie znaleziono linku 'Twoje produkty Allegro', wpisuję URL bezpośrednio...")
            page.goto("https://gapli.com/dashboard/products/allegro", wait_until="networkidle")
            
        time.sleep(10)
        
        # Filtrujemy przechwycone zapytania pod kątem produktów
        relevant = [r for r in captured_requests if "products" in r["url"]]
        
        with open("allegro_products_api_discovery.json", "w", encoding="utf-8") as f:
            json.dump(relevant, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Zapisano {len(relevant)} istotnych zapytań do allegro_products_api_discovery.json")

    except Exception as e:
        logger.error(f"Błąd: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    discover_allegro_products_page()

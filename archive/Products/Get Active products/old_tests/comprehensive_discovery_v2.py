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

def comprehensive_discovery():
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

    captured_data = []

    def handle_response(response):
        url = response.url
        if "/api/" in url:
            try:
                if "application/json" in response.headers.get("content-type", ""):
                    data = response.json()
                    captured_data.append({
                        "url": url,
                        "status": response.status_code,
                        "data": data
                    })
                    # Save every 5 responses just in case
                    if len(captured_data) % 5 == 0:
                        with open("comprehensive_api_discovery_partial.json", "w", encoding="utf-8") as f:
                            json.dump(captured_data, f, indent=4, ensure_ascii=False)
            except Exception:
                pass

    page.on("response", handle_response)

    try:
        # Odwiedź główne sekcje
        sections = [
            "https://gapli.com/dashboard/products/allegro"
        ]

        for section in sections:
            logger.info(f"Odwiedzam sekcję: {section}")
            try:
                page.goto(section, wait_until="networkidle", timeout=30000)
                time.sleep(10) # Dłuższe czekanie na dane
                page.screenshot(path=f"screenshot_{section.split('/')[-1]}.png")
            except Exception as e:
                logger.warning(f"Timeout lub błąd na {section}: {e}")

        # Zapisz wszystkie przechwycone dane
        with open("comprehensive_api_discovery.json", "w", encoding="utf-8") as f:
            json.dump(captured_data, f, indent=4, ensure_ascii=False)
        logger.info(f"Zapisano {len(captured_data)} zapytań API do comprehensive_api_discovery.json")

    except Exception as e:
        logger.error(f"Błąd podczas discovery: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    comprehensive_discovery()

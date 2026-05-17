import os
import re
import time
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

def discover_endpoints():
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

    discovered_urls = set()
    js_files = set()

    # 1. Nasłuchiwanie na bieżący ruch sieciowy
    def handle_request(request):
        url = request.url
        if "/api/" in url:
            discovered_urls.add(url)
        if url.endswith(".js"):
            js_files.add(url)

    page.on("request", handle_request)

    logger.info("Nawigacja po kluczowych stronach w celu wywołania zapytań API...")
    
    # Lista stron do odwiedzenia
    pages_to_scan = [
        "https://gapli.com/dashboard",
        "https://gapli.com/dashboard/products",
        "https://gapli.com/dashboard/orders",
        "https://gapli.com/dashboard/settings",
        "https://gapli.com/dashboard/integrations",
        "https://gapli.com/dashboard/wholesalers"
    ]

    for target_url in pages_to_scan:
        try:
            logger.info(f"Skanowanie strony: {target_url}")
            page.goto(target_url, wait_until="networkidle", timeout=30000)
            time.sleep(2) # Czekaj na asynchroniczne zapytania
        except Exception as e:
            logger.warning(f"Nie udało się załadować {target_url}: {e}")

    # 2. Analiza plików JavaScript w poszukiwaniu ukrytych endpointów
    logger.info(f"Znaleziono {len(js_files)} plików JavaScript. Analizuję ich zawartość...")
    
    api_pattern = re.compile(r'["\'](/api/v1/[a-zA-Z0-9_\-/:]+)["\']')
    
    for js_url in js_files:
        try:
            # Pomiń biblioteki zewnętrzne (google, facebook, stripe)
            if any(domain in js_url for domain in ["googletagmanager", "facebook", "stripe", "hotjar"]):
                continue
                
            response = requests.get(js_url, timeout=10)
            if response.status_code == 200:
                matches = api_pattern.findall(response.text)
                for match in matches:
                    discovered_urls.add(f"https://gapli.com{match}")
        except Exception:
            pass

    # 3. Zapisanie wyników
    logger.info(f"Skanowanie zakończone. Znaleziono {len(discovered_urls)} potencjalnych endpointów.")
    
    with open("discovered_endpoints.txt", "w", encoding="utf-8") as f:
        f.write("=== ZNALEZIONE ENDPOINTY GAPLI ===\n\n")
        # Sortowanie dla czytelności
        sorted_urls = sorted(list(discovered_urls))
        for url in sorted_urls:
            f.write(f"{url}\n")

    print("\n--- WYNIKI ---")
    print(f"Liczba znalezionych endpointów: {len(discovered_urls)}")
    print("Wyniki zostały zapisane do pliku: discovered_endpoints.txt")
    
    # Sprzątanie
    playwright_instance.stop()

if __name__ == "__main__":
    discover_endpoints()

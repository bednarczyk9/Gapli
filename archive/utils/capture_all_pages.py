import os
import time
import json
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def capture_all_pages_deletion():
    port = 9222
    sku = "1004260-660_150"
    
    logger.info(f"Connecting to Chrome on port {port}...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0]
            
            captured_requests = []

            # Listener for all pages in this context (including your existing tabs)
            def on_request(request):
                if "/api/" in request.url:
                    captured_requests.append({
                        "method": request.method,
                        "url": request.url,
                        "post_data": request.post_data,
                        "headers": dict(request.headers)
                    })

            # Attach listener to all current and future pages
            for page in context.pages:
                page.on("request", on_request)
            
            context.on("page", lambda page: page.on("request", on_request))

            print("\n" + "="*60)
            print("!!! NASŁUCHUJĘ NA WSZYSTKICH KARTACH !!!")
            print(f"1. Przejdź do swojej karty z Gapli.")
            print(f"2. KLIKNIJ 'USUŃ' DLA SKU {sku}.")
            print("="*60)
            print("\nCzekam 60 sekund...")
            
            time.sleep(60)
            
            print("\nANALIZA PRZECHWYCONEGO RUCHU:")
            found = False
            for req in captured_requests:
                u = req["url"].lower()
                if "customization" in u or sku in u:
                    found = True
                    print("-" * 40)
                    print(f"METODA: {req['method']}")
                    print(f"URL:    {req['url']}")
                    if req["post_data"]:
                        print(f"DATA:   {req['post_data']}")
            
            if not found:
                print("Niestety nic nie złapałem. Upewnij się, że operacja usuwania faktycznie wysyła zapytanie do API.")
            
            # Note: browser.close() might close your browser, so we'll just disconnect
        except Exception as e:
            logger.error(f"Błąd połączenia: {e}")

if __name__ == "__main__":
    capture_all_pages_deletion()

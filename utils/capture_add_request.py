import os
import time
import json
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def capture_add_request():
    port = 9222
    
    logger.info(f"Connecting to Chrome on port {port}...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0]
            
            captured_requests = []

            def on_request(request):
                if "/api/" in request.url:
                    captured_requests.append({
                        "method": request.method,
                        "url": request.url,
                        "post_data": request.post_data,
                        "headers": dict(request.headers)
                    })

            for page in context.pages:
                page.on("request", on_request)
            
            context.on("page", lambda page: page.on("request", on_request))

            print("\n" + "="*60)
            print("!!! NASŁUCHUJĘ NA WSZYSTKICH KARTACH !!!")
            print("1. Otwórz Gapli Marketplace.")
            print("2. Zaznacz kilka produktów.")
            print("3. Kliknij 'Wyślij zaznaczone produkty'.")
            print("4. Wybierz konto i kliknij 'Wyślij na Allegro'.")
            print("="*60)
            print("\nCzekam 60 sekund...")
            
            time.sleep(60)
            
            print("\nANALIZA PRZECHWYCONEGO RUCHU:")
            found = False
            for req in captured_requests:
                u = req["url"].lower()
                # Looking for anything related to marketplace, listing, products, send
                if "marketplace" in u or "listing" in u or "send" in u or "product" in u:
                    if req["method"] == "POST":
                        found = True
                        print("-" * 40)
                        print(f"METODA: {req['method']}")
                        print(f"URL:    {req['url']}")
                        if req["post_data"]:
                            print(f"DANE:   {req['post_data']}")
                        print(f"HEADERS: {json.dumps(req['headers'], indent=2)}")
            
            if not found:
                print("Nie przechwycono żadnych zapytań o dodawanie produktów.")
            
        except Exception as e:
            logger.error(f"Błąd połączenia: {e}")

if __name__ == "__main__":
    capture_add_request()

import os
import time
import json
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def capture_controlled():
    port = 9222
    logger.info(f"Connecting to Chrome on port {port} and opening NEW CONTROLLED TAB...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0]
            
            # Open a fresh tab that I definitely control
            page = context.new_page()
            
            captured = []
            def on_request(request):
                if "/api/" in request.url:
                    captured.append({
                        "method": request.method,
                        "url": request.url,
                        "data": request.post_data
                    })

            page.on("request", on_request)
            page.goto("https://gapli.com/dashboard/product-customizer")

            print("\n" + "="*60)
            print("!!! NOWA KARTA OTWARTA !!!")
            print("1. Zaloguj się (jeśli trzeba) i przejdź do usuwania.")
            print("2. Wykonaj operację 'Usuń' w TEJ konkretnej karcie.")
            print("="*60)
            
            time.sleep(120) # 2 minutes
            
            print(f"\nAnaliza ruchu z kontrolowanej karty ({len(captured)} zapytań):")
            for req in captured:
                if "customization" in req["url"].lower():
                    print(f"[{req['method']}] {req['url']}")
                    if req['data']: print(f"  DATA: {req['data']}")

        except Exception as e:
            logger.error(f"Błąd: {e}")

if __name__ == "__main__":
    capture_controlled()

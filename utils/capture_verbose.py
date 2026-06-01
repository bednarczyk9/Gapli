import os
import time
import json
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def capture_everything():
    port = 9222
    logger.info(f"Connecting to Chrome on port {port}...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0]
            
            captured = []

            def on_request(request):
                # Catch EVERY request to see what's happening
                captured.append({
                    "method": request.method,
                    "url": request.url,
                    "data": request.post_data
                })

            for page in context.pages:
                page.on("request", on_request)
            
            context.on("page", lambda page: page.on("request", on_request))

            print("\n" + "="*60)
            print("!!! PRZECHWYTYWANIE KAŻDEGO RUCHU (60 SEKUND) !!!")
            print("Wykonaj teraz operację usuwania w Gapli.")
            print("="*60)
            
            time.sleep(60)
            
            print(f"\nPrzechwycono łącznie {len(captured)} zapytań.")
            print("\nOstatnie 20 zapytań:")
            for req in captured[-20:]:
                print(f"[{req['method']}] {req['url'][:100]}")
                if req['data'] and "customization" in str(req['data']).lower():
                    print(f"  -> DANE ZAWIERAJĄ 'customization': {req['data']}")

        except Exception as e:
            logger.error(f"Błąd: {e}")

if __name__ == "__main__":
    capture_everything()

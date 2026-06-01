import os
import time
import json
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def capture_delete_api_resume():
    sku = "1004260-660_150"
    port = 9222
    
    logger.info(f"Connecting to existing Chrome on port {port}...")
    
    with sync_playwright() as p:
        try:
            # 1. Connect to the browser that user already has open and logged in
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0]
            
            # Use an existing page if possible, or create a new tab in the SAME context
            page = context.new_page()
            
            captured_requests = []
            def handle_request(request):
                if "/api/" in request.url:
                    captured_requests.append({
                        "method": request.method,
                        "url": request.url,
                        "post_data": request.post_data,
                        "headers": dict(request.headers)
                    })
            
            page.on("request", handle_request)
            
            print("\n" + "="*60)
            print("!!! SESJA WZNOWIONA !!!")
            print(f"1. W otwartym oknie Chrome usuń nadpisanie dla SKU {sku}.")
            print("2. Ja przechwytuję ruch w tle.")
            print("="*60)
            print("\nCzekam 60 sekund na Twoją akcję...")
            
            # Wait for user action
            time.sleep(60)
            
            print("\nPrzechwycone zapytania (szukamy DELETE lub POST/PATCH do customizations):")
            found_any = False
            for req in captured_requests:
                url_low = req["url"].lower()
                if "customization" in url_low or sku in url_low:
                    found_any = True
                    print("-" * 40)
                    print(f"METODA:  {req['method']}")
                    print(f"URL:     {req['url']}")
                    if req["post_data"]:
                        print(f"DANE:    {req['post_data']}")
                    if "authorization" in req["headers"]:
                        print(f"AUTH:    Bearer {req['headers']['authorization'][:20]}...")
            
            if not found_any:
                print("Brak zapytań. Czy na pewno kliknąłeś 'Usuń'?")
                
            browser.close()
        except Exception as e:
            logger.error(f"Nie udało się połączyć z przeglądarką: {e}")
            print("Upewnij się, że Chrome jest uruchomiony z flagą --remote-debugging-port=9222")

if __name__ == "__main__":
    capture_delete_api_resume()

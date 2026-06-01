import os
import time
import json
import logging
import subprocess
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def capture_delete_api():
    sku = "1004260-660_150"
    port = 9222
    
    # 1. Start Chrome with remote debugging (as in ChromeManager)
    # Using taskkill first to ensure clean state
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
    
    profile_path = os.path.join(os.environ.get("TEMP", "."), "chrome-capture")
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    chrome_args = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_path}",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    
    logger.info("Starting Chrome for capture...")
    subprocess.Popen(chrome_args)
    time.sleep(5)
    
    with sync_playwright() as p:
        # 2. Connect Playwright to the existing Chrome instance
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        context = browser.contexts[0]
        page = context.new_page()
        
        captured_requests = []
        def handle_request(request):
            if "/api/" in request.url:
                captured_requests.append({
                    "method": request.method,
                    "url": request.url,
                    "post_data": request.post_data,
                    "headers": request.headers
                })
        
        page.on("request", handle_request)
        
        logger.info("Navigating to Gapli...")
        page.goto("https://gapli.com/login")
        
        print("\n" + "="*60)
        print("!!! INSTRUKCJA DLA CIEBIE !!!")
        print("1. Zaloguj się w otwartym oknie Chrome.")
        print(f"2. Przejdź do edycji produktu {sku}.")
        print("3. Wykonaj operację USUNIĘCIA nadpisania.")
        print("4. Ja będę w tle przechwytywał ruch sieciowy.")
        print("="*60)
        print("\nCzekam 120 sekund na Twoją akcję...")
        
        # Extended wait time for manual login and navigation
        time.sleep(120)
        
        print("\nCaptured API calls related to customizations:")
        found_any = False
        for req in captured_requests:
            if "customization" in req["url"].lower() or sku in req["url"]:
                found_any = True
                print("-" * 40)
                print(f"METHOD: {req['method']}")
                print(f"URL:    {req['url']}")
                if req["post_data"]:
                    print(f"DATA:   {req['post_data']}")
                # Look for specific headers that might be required
                if "x-csrf-token" in req["headers"]:
                    print(f"CSRF:   {req['headers']['x-csrf-token']}")
        
        if not found_any:
            print("Nie przechwycono żadnych zapytań o nadpisania. Spróbuj zwiększyć czas oczekiwania.")

        browser.close()

if __name__ == "__main__":
    capture_delete_api()

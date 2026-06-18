import os
import time
import json
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def capture_search_api():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Login
        page.goto("https://gapli.com/login")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button:has-text("Zaloguj się")')
        page.wait_for_url("**/dashboard**")
        
        captured_requests = []
        def handle_request(request):
            if "/api/" in request.url:
                captured_requests.append({
                    "method": request.method,
                    "url": request.url,
                    "post_data": request.post_data
                })
        
        page.on("request", handle_request)
        
        # Search for a global EAN (iPhone 15 or something common)
        ean = "195949048388" # iPhone 15 Pro Max EAN
        search_url = f"https://gapli.com/dashboard/products/allegro?search={ean}"
        logger.info(f"Searching for {ean}...")
        page.goto(search_url)
        time.sleep(10) # Wait for all lazy loads
        
        print("\nCaptured API calls during search:")
        for req in captured_requests:
            url = req["url"]
            if ean in url or "search" in url.lower() or "allegro" in url.lower():
                print(f"{req['method']} {url}")
                if req["post_data"]:
                    print(f"  Data: {req['post_data']}")
        
        browser.close()

if __name__ == "__main__":
    capture_search_api()

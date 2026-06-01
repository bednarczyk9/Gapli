import os
import time
import json
import logging
from playwright.sync_api import sync_playwright
from keywords.gapli_keywords import start_browser_and_login

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def capture_search_api():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")
    
    with sync_playwright() as p:
        # Use existing start_browser_and_login if possible or just manual
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Login
        page.goto("https://gapli.com/login")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button:has-text("Zaloguj się")')
        page.wait_for_url("**/dashboard**")
        
        captured_urls = []
        def handle_request(request):
            if "/api/" in request.url:
                captured_urls.append(request.url)
        
        page.on("request", handle_request)
        
        # Navigate to Allegro products and search by EAN
        ean = "5702017155531" # LEGO Dagobah
        search_url = f"https://gapli.com/dashboard/products/allegro?search={ean}"
        logger.info(f"Searching for {ean}...")
        page.goto(search_url)
        time.sleep(5)
        
        # Look for "Add from Allegro" or similar buttons
        # In Gapli, there is often a way to search the catalog.
        
        print("Captured API calls during search:")
        for url in captured_urls:
            if ean in url or "catalog" in url.lower() or "search" in url.lower():
                print(url)
        
        browser.close()

if __name__ == "__main__":
    capture_search_api()

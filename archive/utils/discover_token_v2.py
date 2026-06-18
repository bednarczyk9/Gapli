import os
import time
import json
import logging
from playwright.sync_api import sync_playwright
from libraries.chrome_manager import ChromeManager
from libraries.gapli_client import GapliClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def discover_token_with_chrome_manager():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")
    
    if not username or not password:
        logger.error("GAPLI_USER or ERROR: GAPLI_PASS not set.")
        return

    chrome = ChromeManager()
    if not chrome.start_chrome():
        logger.error("Failed to start Chrome.")
        return

    token = None

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = context.new_page()
        
        def handle_request(request):
            nonlocal token
            auth = request.headers.get("authorization")
            if auth and "Bearer" in auth:
                token = auth

        page.on("request", handle_request)
        
        client = GapliClient(page)
        logger.info("Logging into Gapli...")
        if client.login(username, password):
            logger.info("Login successful.")
            logger.info("Navigating to marketplace...")
            page.goto("https://gapli.com/dashboard/marketplace/products")
            time.sleep(5)
            
            if token:
                logger.info("Successfully captured Bearer token.")
                print(f"\nTOKEN_FOUND={token}\n")
            else:
                logger.error("Could not capture Bearer token.")
        else:
            logger.error("Login failed.")
            
        browser.close()
    
    chrome.stop_chrome()

if __name__ == "__main__":
    discover_token_with_chrome_manager()

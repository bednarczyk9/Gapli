import os
import time
import json
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def discover_token_and_endpoints():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")
    
    if not username or not password:
        logger.error("GAPLI_USER or GAPLI_PASS not set.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        token = None
        
        def handle_request(request):
            nonlocal token
            auth = request.headers.get("authorization")
            if auth and "Bearer" in auth:
                token = auth
                # logger.info(f"Captured token: {token[:30]}...")

        page.on("request", handle_request)
        
        logger.info("Logging into Gapli...")
        page.goto("https://gapli.com/login")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button:has-text("Zaloguj się")')
        
        try:
            page.wait_for_url("**/dashboard**", timeout=30000)
            logger.info("Login successful.")
        except:
            logger.error("Login failed or timed out.")
            browser.close()
            return

        # Navigate to marketplace to trigger API calls
        logger.info("Navigating to marketplace...")
        page.goto("https://gapli.com/dashboard/marketplace/products")
        time.sleep(5) # Wait for requests
        
        if token:
            logger.info("Successfully captured Bearer token.")
            # Verify some endpoints
            headers = {"Authorization": token, "Content-Type": "application/json"}
            
            # 1. Accounts
            resp = page.request.get("https://gapli.com/api/v1/integrations/marketplace/accounts", headers=headers)
            if resp.status_code == 200:
                logger.info("Accounts endpoint verified.")
                # logger.info(f"Accounts: {resp.json().get('accounts', [])}")
            else:
                logger.warning(f"Accounts endpoint failed: {resp.status_code}")
                
            # 2. Wholesalers
            resp = page.request.get("https://gapli.com/api/v1/integrations/wholesalers", headers=headers)
            if resp.status_code == 200:
                logger.info("Wholesalers endpoint verified.")
            else:
                logger.warning(f"Wholesalers endpoint failed: {resp.status_code}")
                
            print(f"\nTOKEN_FOUND={token}\n")
        else:
            logger.error("Could not capture Bearer token.")
            
        browser.close()

if __name__ == "__main__":
    discover_token_and_endpoints()

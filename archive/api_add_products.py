import os
import requests
import json
import logging
import time
from datetime import datetime
import openpyxl
from playwright.sync_api import sync_playwright

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
# Based on add_products.py and typical project usage
STORES = ["AlejaOkazji", "hit_bazar", "radosnydzieciak", "skarbiec_ofert"] 
WHOLESALERS_FILE = "Recorded/hurtownie_allegro.xlsx"

CONFIG = {
    'min_price': 50,    # min_price_filter from add_products.py
    'max_price': 50000,
    'min_stock': 2
}

class GapliAPIClient:
    def __init__(self, token):
        # Ensure token is in Bearer format
        if token and not token.startswith("Bearer "):
            self.token = f"Bearer {token}"
        else:
            self.token = token
            
        self.base_url = "https://gapli.com/api/v1/integrations"
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_accounts(self):
        """Fetches marketplace accounts."""
        url = f"{self.base_url}/marketplace/accounts"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("accounts", [])

    def get_wholesalers(self):
        """Fetches wholesalers (parsers)."""
        url = f"{self.base_url}/wholesalers"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("wholesalers", [])

    def get_products(self, parser_id, min_price, max_price, min_stock):
        """Fetches products from a specific wholesaler based on criteria."""
        url = f"{self.base_url}/products"
        all_products = []
        offset = 0
        limit = 500 # Smaller limit for better stability

        params = {
            "parser_id": parser_id,
            "price_gross_min": min_price,
            "price_gross_max": max_price,
            "stock_min": min_stock,
            "available": "true",
            "limit": limit
        }

        while True:
            params["offset"] = offset
            logger.info(f"Fetching products (parser_id: {parser_id}, offset: {offset})...")
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=60)
                if response.status_code == 500:
                    logger.warning("Server error (500) during fetch. Retrying in 10s...")
                    time.sleep(10)
                    continue
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logger.error(f"Error fetching products: {e}")
                break
            
            products = data.get("products", [])
            if not products:
                break
                
            # Filter out allegro_blocked locally if not supported by API
            valid_products = [p for p in products if not p.get('allegro_blocked', False)]
            all_products.extend(valid_products)
            
            if not data.get("pagination", {}).get("has_more", False):
                break
                
            offset += len(products)
            time.sleep(0.3) 

        return all_products

    def send_to_marketplace(self, account_id, skus, min_price, max_price):
        """Sends products to the marketplace account."""
        url = f"{self.base_url}/marketplace/listing"
        
        # Batching SKUs (max 100 per request)
        batch_size = 100
        for i in range(0, len(skus), batch_size):
            batch = skus[i:i + batch_size]
            body = {
                "action": "send",
                "account_id": account_id,
                "product_skus": batch,
                "price_range": {
                    "min": min_price,
                    "max": max_price
                }
            }
            
            retries = 3
            while retries > 0:
                logger.info(f"Sending batch of {len(batch)} products to account {account_id}...")
                try:
                    response = requests.post(url, headers=self.headers, json=body, timeout=60)
                    
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", 30))
                        logger.warning(f"Rate limit hit! Waiting {retry_after}s...")
                        time.sleep(retry_after)
                        continue
                    
                    if response.status_code == 500:
                        logger.warning("Internal server error (500). Retrying in 15s...")
                        time.sleep(15)
                        retries -= 1
                        continue

                    if response.status_code != 200:
                        logger.error(f"Failed to send batch: {response.status_code} {response.text}")
                        break
                        
                    logger.info(f"API Response: {response.json().get('message', 'Success')}")
                    break
                except Exception as e:
                    logger.error(f"Network error during send: {e}")
                    time.sleep(5)
                    retries -= 1
            
            time.sleep(0.5)

def get_token_via_browser():
    """Attempts to capture a Bearer token by logging in via Playwright."""
    logger.warning("!!! ATTENTION: Browser login might trigger CAPTCHA. Please be ready to solve it if a browser window stays open !!!")
    # Import locally to avoid dependency issues if not needed
    try:
        from libraries.chrome_manager import ChromeManager
        from libraries.gapli_client import GapliClient
    except ImportError:
        logger.error("Required libraries (ChromeManager, GapliClient) not found.")
        return None

    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")
    
    if not username or not password:
        logger.error("GAPLI_USER or GAPLI_PASS environment variables not set.")
        return None

    chrome = ChromeManager()
    if not chrome.start_chrome():
        return None

    token = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.new_page()
            
            def on_request(request):
                nonlocal token
                auth = request.headers.get("authorization")
                if auth and "Bearer" in auth:
                    token = auth

            page.on("request", on_request)
            client = GapliClient(page)
            
            logger.info("Logging in to Gapli via browser to capture token...")
            if client.login(username, password):
                # Trigger some API calls
                page.goto("https://gapli.com/dashboard/marketplace/products", wait_until="networkidle")
                time.sleep(3)
                
            browser.close()
    except Exception as e:
        logger.error(f"Error during browser token capture: {e}")
    finally:
        chrome.kill_chrome()
        
    return token

def read_wholesalers(file_path):
    """Reads wholesaler names from Excel."""
    if not os.path.exists(file_path):
        logger.error(f"Wholesalers file not found: {file_path}")
        return []
    
    try:
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        return [row[0] for row in ws.iter_rows(min_row=2, values_only=True) if row[0]]
    except Exception as e:
        logger.error(f"Error reading wholesalers file: {e}")
        return []

def main():
    # 1. Get Authentication
    api_key = os.environ.get("Gapli_Apikey")
    if not api_key:
        logger.info("Gapli_Apikey not found. Attempting browser-based authentication...")
        api_key = get_token_via_browser()
        
    if not api_key:
        logger.error("No valid API key or token found. Exiting.")
        return

    client = GapliAPIClient(api_key)

    # 2. Get Metadata (Accounts and Wholesalers)
    try:
        logger.info("Fetching marketplace accounts...")
        accounts = client.get_accounts()
        store_to_acc = {acc['store_name']: acc['id'] for acc in accounts if acc.get('platform') == 'allegro'}
        
        logger.info("Fetching wholesalers list...")
        api_wholesalers = client.get_wholesalers()
        name_to_parser_id = {w['name']: w['parser_id'] for w in api_wholesalers if w.get('parser_id')}
    except Exception as e:
        logger.error(f"Failed to fetch metadata from API: {e}")
        return

    # 3. Process Wholesalers
    wholesalers_to_process = read_wholesalers(WHOLESALERS_FILE)
    if not wholesalers_to_process:
        logger.warning("No wholesalers found to process.")
        return

    for store_name in STORES:
        account_id = store_to_acc.get(store_name)
        
        # Fuzzy match if exact match fails
        if not account_id:
            for name, acc_id in store_to_acc.items():
                if store_name.lower() in name.lower():
                    account_id = acc_id
                    logger.info(f"Fuzzy matched store '{store_name}' to account '{name}' (ID: {account_id})")
                    break
        
        if not account_id:
            logger.warning(f"Account for store '{store_name}' not found. Skipping.")
            continue
            
        logger.info(f"=== PROCESSING STORE: {store_name} (ID: {account_id}) ===")
        
        for w_name in wholesalers_to_process:
            parser_id = name_to_parser_id.get(w_name)
            if not parser_id:
                logger.warning(f"Wholesaler '{w_name}' not found in Gapli (no parser_id).")
                continue
                
            logger.info(f"--- Wholesaler: {w_name} (ID: {parser_id}) ---")
            
            try:
                products = client.get_products(
                    parser_id, 
                    CONFIG['min_price'], 
                    CONFIG['max_price'], 
                    CONFIG['min_stock'],
                    account_id=account_id
                )
                
                if not products:
                    logger.info(f"No products found for {w_name} with current filters.")
                    continue
                
                skus = [p['sku'] for p in products if p.get('sku')]
                logger.info(f"Found {len(skus)} products. Sending to marketplace...")
                
                client.send_to_marketplace(
                    account_id, 
                    skus, 
                    CONFIG['min_price'], 
                    CONFIG['max_price']
                )
                
            except Exception as e:
                logger.error(f"Error processing {w_name}: {e}")

    logger.info("All tasks completed.")

if __name__ == "__main__":
    main()

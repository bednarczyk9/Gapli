import os
import time
import json
import logging
import subprocess
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_gapli_token():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")
    
    if not username or not password:
        logger.error("GAPLI_USER or GAPLI_PASS not set.")
        return None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        token = None
        def handle_request(request):
            nonlocal token
            auth = request.headers.get("authorization")
            if auth and "Bearer" in auth and "eyJ" in auth:
                token = auth

        page.on("request", handle_request)
        
        logger.info("Logging into Gapli...")
        page.goto("https://gapli.com/login")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button:has-text("Zaloguj się")')
        
        try:
            page.wait_for_url("**/dashboard**", timeout=20000)
            logger.info("Login successful.")
            
            # Navigate to marketplace to trigger API calls
            page.goto("https://gapli.com/dashboard/products/allegro?konto_allegro_id=116&status=DRAFT")
            page.wait_for_timeout(5000)
        except Exception as e:
            logger.error(f"Login/Navigation failed: {e}")
            
        browser.close()
        return token

def bulk_delete_drafts(token):
    if not token:
        return
        
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # 1. Fetch DRAFT products to see their IDs
    account_id = 116
    print(f"Fetching drafts for account {account_id}...")
    # Use pagination to get more
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={account_id}&status=DRAFT&limit=100"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f"Failed to fetch drafts: {resp.status_code} {resp.text}")
        return

    data = resp.json()
    products = data.get("products", [])
    total = data.get("total", 0)
    print(f"Total drafts found in Gapli: {total}")
    
    if not products:
        print("No drafts found in Gapli for this account.")
        return

    product_ids = [p.get("id") for p in products]
    print(f"Attempting to delete {len(product_ids)} products...")
    
    # Gapli usually has a bulk delete endpoint.
    # From discovery, it might be a POST to some endpoint with a list of IDs.
    # Or multiple DELETE requests.
    # Let's try the common bulk endpoint if we can find it.
    
    # Discovery script mentioned: https://gapli.com/api/v1/integrations/marketplace/listing with action: remove
    # But that might be for the other API.
    
    # Let's try to delete them one by one if bulk is not known.
    success_count = 0
    for p_id in product_ids:
        del_url = f"https://gapli.com/api/products-manager/allegro/products/{p_id}"
        del_resp = requests.delete(del_url, headers=headers)
        if del_resp.status_code in [200, 204]:
            success_count += 1
        else:
            print(f"Failed to delete {p_id}: {del_resp.status_code}")
            
    print(f"Successfully deleted {success_count} products from Gapli.")

import requests

if __name__ == "__main__":
    token = get_gapli_token()
    if token:
        print(f"Obtained token: {token[:50]}...")
        bulk_delete_drafts(token)
    else:
        print("Failed to obtain token.")

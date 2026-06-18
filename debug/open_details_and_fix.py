import time
import os
import logging
import sys
from playwright.sync_api import sync_playwright

# Add current and archive directory to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "archive"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def open_details_and_fix():
    sku = "1053851_131"
    
    with sync_playwright() as p:
        try:
            logger.info("Connecting to active browser...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            
            page = None
            for p_obj in context.pages:
                if "gapli.com" in p_obj.url:
                    page = p_obj
                    break
            
            if not page:
                logger.error("Gapli page not found.")
                return

            # 1. Search if not already searched
            logger.info(f"Ensuring SKU {sku} is searched...")
            search_input = page.locator("input[placeholder*='Szukaj'], input[placeholder*='Search']").first
            if search_input.is_visible():
                search_input.fill("")
                search_input.fill(sku)
                search_input.press("Enter")
                time.sleep(5)
            
            # 2. Click the row to open details
            logger.info(f"Clicking row for SKU {sku}...")
            # We target the row or the product name inside it
            row = page.locator(f"tr:has-text('{sku}')").first
            if row.is_visible():
                row.click()
                time.sleep(5)
                logger.info("Details view should be open.")
            else:
                logger.error("Row not found.")
                return

            # 3. Perform Sync from Catalog
            sync_btn = page.locator("button:has-text('Synchronizuj dane z Gapli')").first
            if sync_btn.is_visible():
                logger.info("Clicking 'Synchronizuj dane z Gapli'...")
                sync_btn.click()
                time.sleep(10)
                
                # 4. Trigger Send
                send_btn = page.locator("button:has-text('Wyślij do Allegro'), button:has-text('Retry'), button:has-text('Ponów')").first
                if send_btn.is_visible():
                    logger.info(f"Clicking {send_btn.inner_text()}...")
                    send_btn.click()
                    time.sleep(5)
                    logger.info("SUCCESS!")
                else:
                    logger.error("Send button not found after sync.")
            else:
                logger.error("Sync from catalog button not found in details view.")
                page.screenshot(path="debug_details_fail.png")

        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    open_details_and_fix()

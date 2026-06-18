import time
import os
import logging
import sys
from playwright.sync_api import sync_playwright

# Add current and libs directory to path
sys.path.append(os.getcwd())

from libs.chrome_manager import ChromeManager
from libs.gapli_client import GapliClient
from libs.product_automation import ProductAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def force_ui_sync():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    sku = "1053851_131"
    store_name = "AlejaOkazji"

    chrome = ChromeManager()
    logger.info("Starting Chrome...")
    if not chrome.start_chrome():
        logger.error("Failed to start Chrome.")
        return

    try:
        with sync_playwright() as p:
            logger.info("Connecting to Chrome via CDP...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            client = GapliClient(page)
            automation = ProductAutomation(page, client, username, password)
            
            logger.info("Logging into Gapli...")
            if not client.login(username, password):
                logger.error("Login failed.")
                return

            # Method: Use the Marketplace with AlejaOkazji account specifically selected
            logger.info(f"Navigating to marketplace for {store_name}...")
            # Navigate to the marketplace page for AlejaOkazji (ID 116)
            page.goto("https://gapli.com/dashboard/products/allegro?konto_allegro_id=116", wait_until="networkidle")
            time.sleep(10)
            
            # Robust Search
            logger.info(f"Searching for SKU {sku}...")
            search_input = page.locator("input[placeholder*='Szukaj'], input[placeholder*='Search']").first
            search_input.fill("")
            search_input.fill(sku)
            search_input.press("Enter")
            time.sleep(10) # Wait for search results
            
            page.screenshot(path="debug_marketplace_search_results.png")
            
            # Find the row containing the SKU
            # We look for a table row that has the SKU text
            row = page.locator(f"tr:has-text('{sku}')").first
            if row.is_visible():
                logger.info(f"Found row for SKU {sku}.")
                
                # Check for sync button (cloud icon or title 'Aktualizuj')
                sync_btn = row.locator("button[title*='Aktualizuj'], button[title*='Sync']").first
                if sync_btn.is_visible():
                    logger.info("Clicking sync button...")
                    sync_btn.click()
                    time.sleep(10) # Wait for sync process
                    page.screenshot(path="debug_after_sync_click_v5.png")
                    logger.info("Sync triggered successfully.")
                else:
                    logger.warning("Direct sync button not found. Checking 'Actions' menu.")
                    actions_btn = row.locator("button[aria-haspopup='menu']").first
                    if actions_btn.is_visible():
                        actions_btn.click()
                        time.sleep(3)
                        page.screenshot(path="debug_actions_menu_v5.png")
                        
                        # Find 'Aktualizuj' in the menu
                        menu_item = page.locator("div[role='menu'] button:has-text('Aktualizuj'), li:has-text('Aktualizuj')").first
                        if menu_item.is_visible():
                            logger.info("Clicking 'Aktualizuj' from menu...")
                            menu_item.click()
                            time.sleep(10)
                            page.screenshot(path="debug_after_menu_click_v5.png")
                        else:
                            logger.error("Could not find 'Aktualizuj' in the actions menu.")
                    else:
                        logger.error("No sync button and no actions menu found.")
            else:
                logger.error(f"Row for SKU {sku} still not visible after search.")
                # Maybe it's under 'Wysłane' tab?
                logger.info("Checking if it's under 'Produkty dodane' tab...")
                sent_tab = page.locator("button:has-text('Produkty dodane')").first
                if sent_tab.is_visible():
                    sent_tab.click()
                    time.sleep(10)
                    # Search again
                    search_input.fill("")
                    search_input.fill(sku)
                    search_input.press("Enter")
                    time.sleep(10)
                    page.screenshot(path="debug_sent_tab_search.png")
                    row = page.locator(f"tr:has-text('{sku}')").first
                    if row.is_visible():
                         logger.info("Found product in 'Produkty dodane' tab.")
                         # Click sync here
                         sync_btn = row.locator("button[title*='Aktualizuj'], button[title*='Sync']").first
                         if sync_btn.is_visible():
                             sync_btn.click()
                             time.sleep(10)
                             logger.info("Sync triggered from 'Produkty dodane' tab.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Closing Chrome...")
        chrome.kill_chrome()

if __name__ == "__main__":
    force_ui_sync()

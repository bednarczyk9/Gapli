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

            logger.info(f"Navigating to marketplace for {store_name}...")
            # Navigate to the main listing first
            page.goto("https://gapli.com/dashboard/products/allegro?konto_allegro_id=116", wait_until="networkidle")
            time.sleep(5)
            
            # Clear search if any and enter SKU
            search_input = page.locator("input[placeholder*='Szukaj'], input[placeholder*='Search']").first
            if search_input.is_visible():
                logger.info(f"Entering SKU {sku} into search...")
                search_input.fill("")
                search_input.fill(sku)
                search_input.press("Enter")
                time.sleep(5)
            else:
                logger.warning("Search input not found, trying direct URL again but with more wait.")
                target_url = f"https://gapli.com/dashboard/products/allegro?konto_allegro_id=116&search={sku}"
                page.goto(target_url, wait_until="networkidle")
                time.sleep(10)
            
            page.screenshot(path="debug_gapli_sku_search_v3.png")
            
            # Find the product row
            # Let's use a more robust locator
            product_row = page.locator(f"tr:has-text('{sku}')").first
            if not product_row.is_visible():
                # Try to find by EAN if SKU fails
                ean = "5902431053851"
                logger.info(f"SKU search failed, trying EAN: {ean}")
                search_input.fill("")
                search_input.fill(ean)
                search_input.press("Enter")
                time.sleep(5)
                product_row = page.locator(f"tr:has-text('{sku}')").first
                if not product_row.is_visible():
                    logger.error(f"Product {sku} not found on page even after EAN search.")
                    # Let's take a screenshot of what WE DO see
                    page.screenshot(path="debug_not_found.png")
                    return
                
            logger.info(f"Found product row for {sku}.")
            
            # Click the '...' menu or direct action button if visible
            actions_btn = product_row.locator("button[aria-haspopup='menu']").first
            if actions_btn.is_visible():
                logger.info("Opening actions menu...")
                actions_btn.click()
                time.sleep(2)
                page.screenshot(path="debug_actions_menu_open_v3.png")
                
                # Try to find 'Aktualizuj' in the menu
                menu = page.locator("div[role='menu'], ul[role='menu']").first
                update_opt = menu.locator("button:has-text('Aktualizuj'), li:has-text('Aktualizuj')").first
                if not update_opt.is_visible():
                     update_opt = menu.locator("button:has-text('Wyślij ponownie'), li:has-text('Wyślij ponownie')").first
                
                if update_opt.is_visible():
                    logger.info("Clicking 'Aktualizuj' option...")
                    update_opt.click()
                    time.sleep(5)
                    page.screenshot(path="debug_after_update_click_v3.png")
                    logger.info("Update triggered successfully.")
                else:
                    logger.warning("Could not find Update/Sync option in menu.")
            else:
                logger.warning("Actions menu button not found. Looking for direct sync icon.")
                # Gapli sometimes has a cloud icon for sync
                sync_btn = product_row.locator("button[title*='Sync'], button[title*='Aktualizuj']").first
                if sync_btn.is_visible():
                    sync_btn.click()
                    logger.info("Clicked direct sync button.")
                    time.sleep(5)
                    page.screenshot(path="debug_after_direct_sync_v3.png")
                else:
                    logger.error("No sync/update button found in UI.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Closing Chrome...")
        chrome.kill_chrome()

if __name__ == "__main__":
    force_ui_sync()

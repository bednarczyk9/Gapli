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
            # Use the product customizer list to find the product reliably
            # SKU: 1053851_131
            # URL pattern: https://gapli.com/dashboard/product-customizer?sku=1053851_131
            page.goto(f"https://gapli.com/dashboard/product-customizer?sku={sku}", wait_until="networkidle")
            time.sleep(5)
            
            page.screenshot(path="debug_customizer_view.png")
            
            # Find the Edit/Sync button in Customizer
            # Often there's a table with customizations
            row = page.locator(f"tr:has-text('{sku}')").first
            if row.is_visible():
                logger.info("Found product in customizer list.")
                # Look for 'Wymuś synchronizację' or similar in actions
                actions_btn = row.locator("button[aria-haspopup='menu']").first
                if actions_btn.is_visible():
                    actions_btn.click()
                    time.sleep(2)
                    page.screenshot(path="debug_customizer_actions.png")
                    # Try to find sync/update
                    sync_opt = page.locator("div[role='menu'] button:has-text('Synchronizuj')").first
                    if sync_opt.is_visible():
                        sync_opt.click()
                        logger.info("Triggered sync from customizer.")
                        time.sleep(5)
                        page.screenshot(path="debug_after_customizer_sync.png")
                    else:
                        logger.warning("Sync option not found in customizer menu.")
            
            # Alternative: Marketplace view with better search
            logger.info("Trying Marketplace view with SKU parameter...")
            page.goto(f"https://gapli.com/dashboard/products/allegro?search={sku}", wait_until="networkidle")
            time.sleep(10) # Heavy page
            page.screenshot(path="debug_marketplace_sku.png")
            
            # Robust row finding
            rows = page.locator("tr").all()
            target_row = None
            for r in rows:
                text = r.inner_text()
                if sku in text:
                    target_row = r
                    break
            
            if target_row:
                logger.info("Found row in marketplace.")
                # Try to click the sync icon directly
                # It's usually an <i> or <svg> inside a button with title 'Aktualizuj'
                update_btn = target_row.locator("button[title*='Aktualizuj'], button[title*='Sync'], button:has-text('Wyślij')").first
                if update_btn.is_visible():
                    logger.info("Clicking update button...")
                    update_btn.click()
                    time.sleep(5)
                    page.screenshot(path="debug_after_marketplace_click.png")
                else:
                    logger.warning("No direct update button, trying actions menu.")
                    actions_btn = target_row.locator("button[aria-haspopup='menu']").first
                    if actions_btn.is_visible():
                        actions_btn.click()
                        time.sleep(2)
                        update_opt = page.locator("div[role='menu'] button:has-text('Aktualizuj')").first
                        if update_opt.is_visible():
                            update_opt.click()
                            logger.info("Clicked Aktualizuj in actions menu.")
                            time.sleep(5)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Closing Chrome...")
        chrome.kill_chrome()

if __name__ == "__main__":
    force_ui_sync()

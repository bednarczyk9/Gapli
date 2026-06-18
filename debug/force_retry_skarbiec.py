import time
import os
import logging
import sys
from playwright.sync_api import sync_playwright

# Add current and archive directory to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "archive"))

from keywords.gapli_keywords import start_browser_and_login

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def force_retry_skarbiec():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    sku = "1053851_131"
    account_id = "63"

    logger.info("Starting browser and logging in...")
    playwright_instance, page, client = start_browser_and_login(username, password)

    if not page:
        logger.error("Failed to start browser or login.")
        if playwright_instance:
            playwright_instance.stop()
        return

    try:
        # Navigate directly to the product details for Skarbiec
        target_url = f"https://gapli.com/dashboard/products/allegro?konto_allegro_id={account_id}&search={sku}"
        logger.info(f"Navigating to: {target_url}")
        page.goto(target_url, wait_until="networkidle")
        time.sleep(5)
        
        page.screenshot(path="debug_skarbiec_retry_start.png")
        
        # Find the row and the Retry button
        row = page.locator(f"tr:has-text('{sku}')").first
        if row.is_visible():
            logger.info("Found product row.")
            # Look for "Retry" or "Ponów" or an icon with that action
            retry_btn = row.locator("button:has-text('Retry'), button:has-text('Ponów'), button[title*='Retry']").first
            
            if not retry_btn.is_visible():
                # Check for sync/update button
                retry_btn = row.locator("button[title*='Aktualizuj'], button[title*='Sync'], button:has-text('Wyślij')").first
            
            if retry_btn.is_visible():
                logger.info(f"Clicking retry/sync button: {retry_btn.inner_text() or retry_btn.get_attribute('title')}")
                retry_btn.click()
                time.sleep(10)
                page.screenshot(path="debug_skarbiec_after_retry.png")
                logger.info("Retry triggered via UI.")
            else:
                logger.warning("Retry button not found in row. Checking actions menu...")
                actions_btn = row.locator("button[aria-haspopup='menu']").first
                if actions_btn.is_visible():
                    actions_btn.click()
                    time.sleep(2)
                    page.screenshot(path="debug_skarbiec_actions.png")
                    # Try to find 'Wyślij ponownie' or 'Aktualizuj'
                    opt = page.locator("div[role='menu'] button:has-text('Wyślij ponownie'), div[role='menu'] button:has-text('Aktualizuj')").first
                    if opt.is_visible():
                        opt.click()
                        logger.info("Clicked action from menu.")
                        time.sleep(10)
                    else:
                        logger.error("Action not found in menu.")
        else:
            logger.error("Product row not found.")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        logger.info("Closing browser...")
        playwright_instance.stop()

if __name__ == "__main__":
    force_retry_skarbiec()

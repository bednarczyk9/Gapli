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

def force_ui_retry_v2():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    sku = "1053851_131"
    account_id = "63"

    logger.info("Starting browser and logging in...")
    playwright_instance, page, client = start_browser_and_login(username, password)

    if not page:
        if playwright_instance: playwright_instance.stop()
        return

    try:
        # Go to the specific product edit page if possible, or listing with error filter
        target_url = f"https://gapli.com/dashboard/products/allegro?konto_allegro_id={account_id}&search={sku}"
        logger.info(f"Navigating to listing: {target_url}")
        page.goto(target_url, wait_until="networkidle")
        time.sleep(10)
        
        # Click on the product row to open details if needed, 
        # but usually there is a 'Retry' button in the 'Status' column or 'Akcje'
        
        # Take a screenshot to see what's on the screen
        page.screenshot(path="debug_skarbiec_ui_v2.png")
        
        # Look for ANY button that might be a retry
        # In the dump it looked like a 'Retry' button next to the error
        retry_btns = page.locator("button:has-text('Retry'), button:has-text('Ponów')").all()
        logger.info(f"Found {len(retry_btns)} retry buttons.")
        
        for btn in retry_btns:
            if btn.is_visible():
                logger.info("Clicking visible Retry button...")
                btn.click()
                time.sleep(10)
                page.screenshot(path="debug_after_ui_retry.png")
                logger.info("Retry clicked.")
                return

        # If not found, try the 'Actions' menu
        row = page.locator(f"tr:has-text('{sku}')").first
        if row.is_visible():
            actions_btn = row.locator("button[aria-haspopup='menu']").first
            if actions_btn.is_visible():
                actions_btn.click()
                time.sleep(2)
                # Look for 'Wyślij do Allegro'
                send_opt = page.locator("div[role='menu'] button:has-text('Wyślij')").first
                if send_opt.is_visible():
                    send_opt.click()
                    logger.info("Clicked Send from menu.")
                    time.sleep(10)
                    return
        
        logger.error("Could not trigger retry via UI.")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    force_ui_retry_v2()

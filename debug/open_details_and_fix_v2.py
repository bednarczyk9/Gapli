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

def open_details_and_fix_v2():
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

            # Click the text of the SKU directly
            logger.info(f"Clicking on text '{sku}'...")
            sku_text = page.get_by_text(sku, exact=False).first
            if sku_text.is_visible():
                sku_text.click()
                time.sleep(5)
                logger.info("Clicked SKU text.")
            else:
                logger.error("SKU text not found.")
                return

            # Perform Sync from Catalog
            sync_btn = page.locator("button:has-text('Synchronizuj dane z Gapli')").first
            if sync_btn.is_visible():
                logger.info("Clicking 'Synchronizuj dane z Gapli'...")
                sync_btn.click()
                time.sleep(10)
                
                # Trigger Send
                send_btn = page.locator("button:has-text('Wyślij do Allegro'), button:has-text('Retry'), button:has-text('Ponów')").first
                if send_btn.is_visible():
                    logger.info(f"Clicking {send_btn.inner_text()}...")
                    send_btn.click()
                    time.sleep(5)
                    logger.info("SUCCESS!")
                else:
                    logger.error("Send button not found.")
            else:
                logger.error("Sync button not found.")
                page.screenshot(path="debug_details_fail_v2.png")

        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    open_details_and_fix_v2()

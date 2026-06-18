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

def force_ui_refresh_skarbiec():
    sku = "1053851_131"
    
    with sync_playwright() as p:
        try:
            logger.info("Connecting to active browser session...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            
            page = None
            for p_obj in context.pages:
                if "gapli.com" in p_obj.url:
                    page = p_obj
                    break
            
            if not page:
                logger.error("Gapli page not found in browser.")
                return

            logger.info(f"Page found: {page.url}")
            
            # 1. Look for 'Synchronizuj dane z Gapli'
            # This is the key button that overwrites the broken cache
            sync_btn = page.locator("button:has-text('Synchronizuj dane z Gapli')").first
            if sync_btn.is_visible():
                logger.info("CLICKING: Synchronizuj dane z Gapli...")
                sync_btn.click()
                time.sleep(10)
                logger.info("Catalog sync completed.")
            else:
                logger.warning("Sync from catalog button not found. Is the product detail view open?")
                page.screenshot(path="debug_not_open.png")
            
            # 2. Look for 'Wyślij do Allegro' or 'Retry'
            send_btn = page.locator("button:has-text('Wyślij do Allegro'), button:has-text('Retry'), button:has-text('Ponów')").first
            if send_btn.is_visible():
                logger.info(f"CLICKING: {send_btn.inner_text()}...")
                send_btn.click()
                time.sleep(10)
                page.screenshot(path="debug_skarbiec_final_push.png")
                logger.info("Push triggered.")
            else:
                logger.error("Send button not found.")

        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    force_ui_refresh_skarbiec()

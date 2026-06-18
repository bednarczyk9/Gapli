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

def retry_skarbiec_specifically():
    sku = "1053851_131"
    account_name = "skarbiec_ofert"
    
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

            logger.info(f"Page URL: {page.url}")
            
            # Find the SKU text element
            sku_loc = page.get_by_text(sku, exact=False).first
            if not sku_loc.is_visible():
                logger.error(f"SKU {sku} not found.")
                return
            
            # Now, find all containers that have this SKU
            # In Gapli, each product on each account is a separate block or row.
            # We want the one that also mentions 'skarbiec_ofert'
            
            # Let's try to find an element that contains BOTH '1053851_131' and 'skarbiec_ofert'
            # Or find the block for skarbiec_ofert first.
            
            logger.info(f"Looking for {sku} under {account_name}...")
            
            # Strategy: find all 'Retry' buttons and check their proximity or container text
            buttons = page.locator("button:has-text('Retry'), button:has-text('Ponów')").all()
            logger.info(f"Found {len(buttons)} retry buttons.")
            
            for btn in buttons:
                # Get the nearest parent that might contain account info
                # Usually it's a few levels up
                parent = btn.locator("xpath=./ancestor::div[contains(@class, 'bg-') or contains(@class, 'rounded')]").first
                if parent.is_visible():
                    text = parent.inner_text().lower()
                    if sku in text and account_name in text:
                        logger.info(f"MATCH FOUND! Clicking Retry for {account_name}...")
                        btn.scroll_into_view_if_needed()
                        btn.click()
                        time.sleep(10)
                        page.screenshot(path="debug_skarbiec_final_retry.png")
                        logger.info("Sync triggered for Skarbiec.")
                        return
            
            logger.warning("Could not find specific Retry button for Skarbiec. Clicking ALL of them just in case.")
            for btn in buttons:
                if btn.is_visible():
                    btn.click()
                    time.sleep(2)
            
            logger.info("Finished triggering retries.")

        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    retry_skarbiec_specifically()

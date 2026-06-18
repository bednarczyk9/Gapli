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

def list_all_actions():
    sku = "1053851_131"
    
    with sync_playwright() as p:
        try:
            logger.info("Connecting to active browser on port 9222...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            
            # Find the page that has Gapli open
            page = None
            for p_obj in context.pages:
                if "gapli.com" in p_obj.url:
                    page = p_obj
                    break
            
            if not page:
                logger.error("Could not find Gapli page.")
                return

            logger.info(f"Connected to page: {page.url}")
            
            # Wait for SKU to be present
            sku_loc = page.get_by_text(sku, exact=False).first
            if not sku_loc.is_visible():
                logger.error(f"SKU {sku} not visible on page. Please make sure it's searched.")
                return
                
            logger.info(f"SKU {sku} found.")
            
            # List all buttons on the page
            buttons = page.locator("button").all()
            logger.info(f"Found {len(buttons)} total buttons on page.")
            
            for i, btn in enumerate(buttons):
                text = btn.inner_text().strip()
                title = btn.get_attribute("title") or ""
                if text or title:
                    # Filter for interesting ones
                    if any(word in (text + title).lower() for word in ["retry", "ponów", "aktualizuj", "wyślij", "sync", "akcje"]):
                        logger.info(f"Button {i}: Text='{text}', Title='{title}'")
            
            # Try to find the row and its buttons
            row = page.locator(f"tr:has-text('{sku}')").first
            if row.is_visible():
                logger.info("Row found. Listing row buttons:")
                row_btns = row.locator("button").all()
                for i, btn in enumerate(row_btns):
                    text = btn.inner_text().strip()
                    title = btn.get_attribute("title") or ""
                    logger.info(f"  Row Button {i}: Text='{text}', Title='{title}'")
                    
                    # If we find a promising button, click it!
                    if any(word in (text + title).lower() for word in ["retry", "ponów", "aktualizuj", "wyślij"]):
                         logger.info(f"CLICKING PROMISING BUTTON: {text or title}")
                         btn.click()
                         time.sleep(5)
                         page.screenshot(path="debug_after_promising_click.png")
                         return

            else:
                logger.warning("Row with SKU not found via 'tr' selector. Trying generic approach...")
                # Search for buttons near the SKU text
                # We'll click the FIRST button that has 'Retry' or 'Ponów' text globally if it's there
                retry = page.locator("button:has-text('Retry'), button:has-text('Ponów')").first
                if retry.is_visible():
                    logger.info("Found global 'Retry' button. Clicking...")
                    retry.click()
                    time.sleep(5)
                    return

        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    list_all_actions()

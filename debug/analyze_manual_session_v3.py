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

def analyze_and_sync_v3():
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
                logger.error("Could not find Gapli page in active browser.")
                return

            logger.info(f"Connected to page: {page.url}")
            
            # Take full page screenshot and dump HTML FIRST
            page.screenshot(path="debug_v3_full.png", full_page=True)
            with open("debug_v3_source.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            
            # Look for SKU text ANYWHERE and find its closest button siblings
            sku_loc = page.get_by_text(sku, exact=False).first
            if sku_loc.is_visible():
                logger.info(f"Found SKU text '{sku}' on page.")
                
                # Let's try to find a button in the same container
                # We'll search for 'Aktualizuj' in the entire page if it's unique enough, 
                # or look for the one closest to the SKU.
                
                # Method 1: Find button by tooltip 'Aktualizuj'
                sync_btn = page.locator("button[title*='Aktualizuj']").first
                if sync_btn.is_visible():
                    logger.info("Found button with 'Aktualizuj' tooltip globally. Clicking...")
                    sync_btn.click()
                    time.sleep(5)
                    page.screenshot(path="debug_v3_after_global_click.png")
                    logger.info("Sync triggered.")
                    return

                # Method 2: Look for '...' actions menu button near the SKU
                # Gapli uses many nested DIVs. Let's try to find the 'Actions' button.
                # It's usually the only button with aria-haspopup or an icon in that row.
                
                logger.info("Looking for actions menu near SKU...")
                # Find all buttons and see which one is closest to the SKU in the DOM or visually
                # For now, let's try a very broad menu search
                menu_btn = page.locator("button[aria-haspopup='menu']").first
                if menu_btn.is_visible():
                    logger.info("Found an actions menu button. Opening...")
                    menu_btn.click()
                    time.sleep(2)
                    page.screenshot(path="debug_v3_menu_open.png")
                    
                    update_opt = page.get_by_text("Aktualizuj").first
                    if update_opt.is_visible():
                        logger.info("Found 'Aktualizuj' in menu. Clicking...")
                        update_opt.click()
                        time.sleep(5)
                        page.screenshot(path="debug_v3_after_menu_click.png")
                        logger.info("Sync triggered via menu.")
                        return
            else:
                logger.error("SKU not found on current page. Is it filtered out or on another tab?")

        except Exception as e:
            logger.error(f"Error in v3: {e}")

if __name__ == "__main__":
    analyze_and_sync_v3()

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

def analyze_and_sync():
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
            
            # 1. Take a screenshot for future reference
            screenshot_path = "debug_manual_session_sku.png"
            page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"Screenshot saved to {screenshot_path}")
            
            # 2. Capture HTML for analysis
            html_content = page.content()
            with open("debug_manual_session_sku.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info("HTML source saved to debug_manual_session_sku.html")
            
            # 3. Continue repair - look for sync/update button in the visible UI
            # We assume the user has already searched for the SKU and it's visible.
            
            row = page.locator(f"tr:has-text('{sku}')").first
            if row.is_visible():
                logger.info(f"Found row for SKU {sku} in UI.")
                
                # Check for direct sync button (cloud icon or title 'Aktualizuj')
                # Looking for buttons with common Gapli sync attributes
                sync_btn = row.locator("button[title*='Aktualizuj'], button[title*='Sync'], button:has-text('Wyślij')").first
                
                if sync_btn.is_visible():
                    logger.info("Triggering sync via direct button...")
                    sync_btn.click()
                    time.sleep(5)
                    page.screenshot(path="debug_after_direct_sync_manual.png")
                    logger.info("Sync action performed.")
                else:
                    logger.info("Direct sync button not found, checking actions menu...")
                    actions_btn = row.locator("button[aria-haspopup='menu']").first
                    if actions_btn.is_visible():
                        actions_btn.click()
                        time.sleep(2)
                        
                        # Find Aktualizuj in the menu
                        update_opt = page.locator("div[role='menu'] button:has-text('Aktualizuj')").first
                        if update_opt.is_visible():
                            update_opt.click()
                            logger.info("Triggered Aktualizuj from actions menu.")
                            time.sleep(5)
                            page.screenshot(path="debug_after_menu_sync_manual.png")
                        else:
                            logger.error("Could not find 'Aktualizuj' option in the menu.")
                    else:
                        logger.error("No sync mechanism identified in the row.")
            else:
                logger.error(f"Row for SKU {sku} is NOT visible on the page. Please ensure it's in view.")

        except Exception as e:
            logger.error(f"Error during manual session analysis: {e}")

if __name__ == "__main__":
    analyze_and_sync()

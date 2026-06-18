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

def analyze_and_sync_v2():
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
            
            # Robust row finding - look for ANY element that contains the SKU text and find its parent TR
            logger.info(f"Searching for SKU {sku} in the DOM...")
            
            # Let's try multiple ways to find the row
            selectors = [
                f"tr:has-text('{sku}')",
                f"tr:has(td:has-text('{sku}'))",
                f"div[role='row']:has-text('{sku}')"
            ]
            
            target_row = None
            for sel in selectors:
                loc = page.locator(sel).first
                if loc.is_visible():
                    target_row = loc
                    logger.info(f"Found row using selector: {sel}")
                    break
            
            if not target_row:
                # Last resort: search for the text directly and find the nearest row-like parent
                sku_element = page.get_by_text(sku, exact=False).first
                if sku_element.is_visible():
                    logger.info("Found SKU text element, looking for parent row...")
                    # Screenshot around the element to see context
                    sku_element.scroll_into_view_if_needed()
                    target_row = sku_element.locator("xpath=./ancestor::tr | ./ancestor::div[@role='row']").first
            
            if target_row and target_row.is_visible():
                logger.info("Target row is confirmed visible.")
                target_row.scroll_into_view_if_needed()
                
                # Check for sync button (cloud icon or title 'Aktualizuj')
                # Often it's a button with a cloud-sync icon
                sync_btn = target_row.locator("button[title*='Aktualizuj'], button[title*='Sync'], button:has-text('Wyślij')").first
                
                if not sync_btn.is_visible():
                    # Try looking for common Gapli icon classes or patterns
                    sync_btn = target_row.locator("button:has(svg), button:has(i)").filter(has_text="").first
                
                if sync_btn.is_visible():
                    tooltip = sync_btn.get_attribute("title")
                    logger.info(f"Found possible sync button with tooltip: '{tooltip}'. Clicking...")
                    sync_btn.click()
                    time.sleep(5)
                    page.screenshot(path="debug_after_sync_click_manual_v2.png")
                    logger.info("Sync action performed.")
                else:
                    logger.info("Direct sync button not found, checking actions menu...")
                    actions_btn = target_row.locator("button[aria-haspopup='menu'], button:has(svg[class*='more']), button:has(i[class*='more'])").first
                    if actions_btn.is_visible():
                        actions_btn.click()
                        time.sleep(2)
                        page.screenshot(path="debug_actions_menu_manual_v2.png")
                        
                        # Find Aktualizuj in the menu
                        update_opt = page.locator("div[role='menu'] button:has-text('Aktualizuj'), li:has-text('Aktualizuj'), [role='menuitem']:has-text('Aktualizuj')").first
                        if update_opt.is_visible():
                            update_opt.click()
                            logger.info("Triggered Aktualizuj from actions menu.")
                            time.sleep(5)
                            page.screenshot(path="debug_after_menu_sync_manual_v2.png")
                        else:
                            logger.error("Could not find 'Aktualizuj' option in the menu.")
                    else:
                        logger.error("No sync mechanism identified in the row.")
            else:
                logger.error(f"SKU {sku} row not found. Current URL is {page.url}.")
                page.screenshot(path="debug_not_found_v2.png")

        except Exception as e:
            logger.error(f"Error during manual session analysis: {e}")

if __name__ == "__main__":
    analyze_and_sync_v2()

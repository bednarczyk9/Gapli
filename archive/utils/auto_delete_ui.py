import os
import time
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def auto_delete_via_ui():
    sku = "1004260-660_150"
    port = 9222
    
    logger.info(f"Connecting to Chrome on port {port} for UI deletion...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0]
            page = context.new_page()
            
            # 1. Go to customization page
            logger.info("Navigating to customization list...")
            page.goto("https://gapli.com/dashboard/product-customizer")
            page.wait_for_load_state("networkidle")
            
            # 2. Search for the SKU
            logger.info(f"Searching for SKU {sku}...")
            # Gapli has two search inputs (desktop/mobile), take the first visible one
            search_input = page.locator("input[placeholder*='SKU'], input[placeholder*='szukaj']").first
            if search_input.is_visible():
                search_input.fill(sku)
                page.keyboard.press("Enter")
                time.sleep(3)
            
            # 3. Find and click the DELETE button (trash icon)
            # We look for a row containing the SKU and then a button inside it
            logger.info("Looking for delete button...")
            row = page.locator(f"tr:has-text('{sku}')").first
            if row.is_visible():
                # Often it's a button with a trash icon or specifically marked
                delete_btn = row.locator("button:has(svg), button[title*='Usuń'], button:has-text('Usuń')").last
                if delete_btn.is_visible():
                    logger.info("Clicking DELETE...")
                    delete_btn.click()
                    
                    # 4. Handle confirmation modal if it appears
                    time.sleep(1)
                    confirm_btn = page.locator("button:has-text('Tak'), button:has-text('Usuń'), button:has-text('Potwierdź')").first
                    if confirm_btn.is_visible():
                        logger.info("Confirming deletion...")
                        confirm_btn.click()
                    
                    logger.info(f"SUCCESS: SKU {sku} deleted via UI.")
                else:
                    logger.error("Could not find delete button in the row.")
            else:
                logger.error(f"SKU {sku} not found in the list.")

            page.close()
        except Exception as e:
            logger.error(f"UI Deletion failed: {e}")

if __name__ == "__main__":
    auto_delete_via_ui()

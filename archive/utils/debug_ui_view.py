import os
import time
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_ui_view():
    sku = "1004260-660_150"
    port = 9222
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0]
            page = context.new_page()
            
            page.goto("https://gapli.com/dashboard/product-customizer")
            time.sleep(5) # Wait for load
            
            # Take screenshot of the list
            page.screenshot(path="debug_customizer.png")
            logger.info("Screenshot saved as debug_customizer.png")
            
            # Try searching again
            search_input = page.locator("input[placeholder*='SKU'], input[placeholder*='szukaj']").first
            search_input.fill(sku)
            page.keyboard.press("Enter")
            time.sleep(5)
            
            # Take screenshot after search
            page.screenshot(path="debug_search_result.png")
            logger.info("Search result screenshot saved as debug_search_result.png")
            
            page.close()
        except Exception as e:
            logger.error(f"Debug failed: {e}")

if __name__ == "__main__":
    debug_ui_view()

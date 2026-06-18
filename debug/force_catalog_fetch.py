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

def force_catalog_fetch():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    product_id = "2977052" # ID for Skarbiec Ofert

    logger.info("Starting browser and logging in...")
    playwright_instance, page, client = start_browser_and_login(username, password)

    if not page:
        if playwright_instance: playwright_instance.stop()
        return

    try:
        # Navigate to product details
        target_url = f"https://gapli.com/dashboard/products/allegro/{product_id}"
        logger.info(f"Navigating to: {target_url}")
        page.goto(target_url, wait_until="networkidle")
        time.sleep(10)
        
        # Look for "Pobierz z katalogu Allegro i zapisz"
        # Based on dump, it's in Section 2
        fetch_btn = page.locator("button:has-text('Pobierz z katalogu Allegro i zapisz')").first
        
        if fetch_btn.is_visible():
            logger.info("Clicking 'Pobierz z katalogu' button...")
            fetch_btn.click()
            time.sleep(10)
            page.screenshot(path="debug_after_catalog_fetch.png")
            logger.info("Catalog fetch triggered.")
            
            # Now trigger the SEND button again (Retry)
            retry_btn = page.locator("button:has-text('Retry'), button:has-text('Ponów')").first
            if retry_btn.is_visible():
                 logger.info("Clicking Retry button after fetch...")
                 retry_btn.click()
                 time.sleep(10)
                 page.screenshot(path="debug_after_all_actions.png")
        else:
            logger.error("Fetch from catalog button not found.")
            # Try to find by index or position if text fails
            buttons = page.locator("button").all()
            for b in buttons:
                if "Pobierz" in b.inner_text():
                    logger.info(f"Found button with 'Pobierz': {b.inner_text()}")
                    b.click()
                    time.sleep(10)
                    break

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    force_catalog_fetch()

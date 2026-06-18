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

def force_sync_from_gapli_catalog():
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
        # Even if the URL doesn't show in the bar, sometimes deep links WORK if navigated directly
        target_url = f"https://gapli.com/dashboard/products/allegro/{product_id}"
        logger.info(f"Navigating to: {target_url}")
        page.goto(target_url, wait_until="networkidle")
        time.sleep(10)
        
        # If it's empty, try the listing and click to open
        if "Brak danych" in page.content() or not page.locator("button").first.is_visible():
             logger.info("Details page seems empty. Navigating to listing and searching...")
             page.goto("https://gapli.com/dashboard/products/allegro?konto_allegro_id=63&search=1053851_131")
             time.sleep(10)
             # Click the row to open details
             page.locator(f"tr:has-text('1053851_131')").first.click()
             time.sleep(5)

        page.screenshot(path="debug_skarbiec_active_view.png")
        
        # Look for "Synchronizuj dane z Gapli"
        sync_btn = page.locator("button:has-text('Synchronizuj dane z Gapli')").first
        if sync_btn.is_visible():
            logger.info("Clicking 'Synchronizuj dane z Gapli'...")
            sync_btn.click()
            time.sleep(10)
            page.screenshot(path="debug_after_catalog_sync.png")
            
            # Now trigger the Allegro Send
            retry_btn = page.locator("button:has-text('Retry'), button:has-text('Ponów'), button:has-text('Wyślij')").first
            if retry_btn.is_visible():
                 logger.info("Triggering Allegro Send...")
                 retry_btn.click()
                 time.sleep(10)
                 page.screenshot(path="debug_skarbiec_final.png")
        else:
            logger.error("Sync button not found.")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    force_sync_from_gapli_catalog()

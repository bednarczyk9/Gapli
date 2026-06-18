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

def force_ui_details_retry():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    product_id = "2977052" # From user dump

    logger.info("Starting browser and logging in...")
    playwright_instance, page, client = start_browser_and_login(username, password)

    if not page:
        if playwright_instance: playwright_instance.stop()
        return

    try:
        # Navigate directly to product details
        target_url = f"https://gapli.com/dashboard/products/allegro/{product_id}"
        logger.info(f"Navigating to details: {target_url}")
        page.goto(target_url, wait_until="networkidle")
        time.sleep(10)
        
        page.screenshot(path="debug_skarbiec_details.png")
        
        # Look for Retry button in details view
        # Based on dump, it might be in section 4 "Synchronizacja Allegro"
        retry_btn = page.locator("button:has-text('Retry'), button:has-text('Ponów')").first
        
        if retry_btn.is_visible():
            logger.info("Clicking Retry button in details...")
            retry_btn.click()
            time.sleep(15)
            page.screenshot(path="debug_after_details_retry.png")
            logger.info("Retry action performed in details view.")
        else:
            logger.error("Retry button not found in details view.")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    force_ui_details_retry()

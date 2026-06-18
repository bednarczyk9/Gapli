import os
import sys
import logging
import time

# Add current and archive directory to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "archive"))

from keywords.gapli_keywords import start_browser_and_login

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def view_product():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    sku = "12014_88"
    account_id = "63" # skarbiec_ofert

    logger.info("Starting browser and logging in...")
    playwright_instance, page, client = start_browser_and_login(username, password)

    if not page:
        logger.error("Failed to login.")
        if playwright_instance: playwright_instance.stop()
        return

    try:
        # Navigate to product list with search
        url = f"https://gapli.com/dashboard/products?konto_allegro_id={account_id}&search={sku}"
        logger.info(f"Navigating to: {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)
        page.screenshot(path="debug_gapli_sku_search.png")
        
        # Check for error message or status
        row = page.locator(f"tr:has-text('{sku}')").first
        if row.is_visible():
            status_text = row.all_text_contents()
            logger.info(f"Product row found: {status_text}")
            
            # Click details
            details_btn = row.locator("a[href*='/dashboard/products/allegro/']").first
            if details_btn.is_visible():
                logger.info("Opening details...")
                details_btn.click()
                time.sleep(5)
                page.screenshot(path="debug_gapli_details.png")
                
                # Try to find the error message
                error_msg = page.locator(".alert-danger, .text-danger").all_text_contents()
                if error_msg:
                    logger.info(f"Found error in UI: {error_msg}")
                
                # Check history/logs
                history_btn = page.locator("a:has-text('Historia'), a:has-text('History')").first
                if history_btn.is_visible():
                    history_btn.click()
                    time.sleep(3)
                    page.screenshot(path="debug_gapli_history.png")
                    
                    # Dump logs text
                    logs = page.locator(".table, .list-group").all_text_contents()
                    logger.info(f"Logs from UI: {logs}")
        else:
            logger.error("SKU not found in UI.")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    view_product()

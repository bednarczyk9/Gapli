import os
import sys
import time
import logging
from playwright.sync_api import sync_playwright

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "archive"))
from keywords.gapli_keywords import start_browser_and_login

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_ean_in_ui():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    sku = "AGDADLWYC0009_33"
    account_id = "61" # Try radosnydzieciak or AlejaOkazji

    logger.info("Logging in...")
    playwright_instance, page, client = start_browser_and_login(username, password)

    if not page:
        logger.error("Failed to login.")
        return

    try:
        p_id = "2965791" # known ID for skarbiec_ofert
        url = f"https://gapli.com/dashboard/products/{p_id}"
        logger.info(f"Going directly to {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)
        
        logger.info("Opened details.")
        
        # We are in details. Let's check Parametry tab
        parametry_tab = page.locator("a.nav-link:has-text('Parametry'), button[role='tab']:has-text('Parametry'), a[role='tab']:has-text('Parametry')").first
        if parametry_tab.is_visible():
            parametry_tab.click()
            time.sleep(3)
            logger.info("Clicked Parametry tab.")
            page.screenshot(path="debug_gapli_params_tab.png")
            
            # Find EAN input and fill it
            ean_input = page.locator("label:has-text('EAN (GTIN)')").locator("xpath=..").locator("input[type='text'], input[type='number']").first
            if ean_input.is_visible():
                val = ean_input.input_value()
                logger.info(f"Current EAN in UI: {val}")
                ean_input.fill("5902934830577")
                
                save_btn = page.locator("button:has-text('Zapisz'), button:has-text('Save')").first
                if save_btn.is_visible():
                    save_btn.click()
                    time.sleep(3)
                    logger.info("Saved params.")
                else:
                    logger.error("Save button not found.")
            else:
                logger.error("EAN input not found in Parametry tab.")
        else:
            logger.error("Parametry tab not found.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    fix_ean_in_ui()

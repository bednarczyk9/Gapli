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

def snap_details():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    
    playwright_instance, page, client = start_browser_and_login(username, password)

    try:
        p_id = "2965791" # known ID for skarbiec_ofert
        url = f"https://gapli.com/dashboard/products/{p_id}"
        logger.info(f"Going directly to {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)
        
        logger.info("Opened details. Snapping...")
        page.screenshot(path="debug_gapli_base_product.png", full_page=True)
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    snap_details()

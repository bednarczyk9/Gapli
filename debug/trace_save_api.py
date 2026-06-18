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

def trace_save_api():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    sku = "AGDADLWYC0009_33"

    logger.info("Logging in...")
    playwright_instance, page, client = start_browser_and_login(username, password)

    if not page:
        logger.error("Failed to login.")
        return

    try:
        url = f"https://gapli.com/dashboard/products/allegro/customizations/edit?sku={sku}"
        page.goto(url, wait_until="networkidle")
        time.sleep(5)
        page.screenshot(path="debug_gapli_cust_edit.png")
        
        # Intercept requests
        def handle_request(request):
            if "customizations" in request.url and request.method in ["POST", "PUT", "PATCH"]:
                try:
                    logger.info(f"CAPTURED REQUEST to {request.url}")
                    logger.info(f"Payload: {request.post_data}")
                except:
                    pass
        
        page.on("request", handle_request)
        
        save_btn = page.locator("button:has-text('Zapisz'), button:has-text('Save')").first
        if save_btn.is_visible():
            save_btn.click()
            time.sleep(5)
            logger.info("Clicked Save.")
        else:
            logger.error("Save button not found.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    trace_save_api()

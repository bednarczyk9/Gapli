import time
import os
import logging
import sys
from playwright.sync_api import sync_playwright

# Add current directory to path
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logger = logging.getLogger(__name__)

def view_error():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    # account 63 (skarbiec_ofert), sku 12014_88 -> product_id 4503385 (approx)
    # I'll search for it
    sku = "12014_88"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        logger.info("Logging in to Gapli...")
        page.goto("https://gapli.com/login")
        page.fill("input[name='email']", username)
        page.fill("input[name='password']", password)
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard**")
        logger.info("Logged in.")

        # Search for product
        logger.info(f"Searching for SKU {sku}...")
        page.goto(f"https://gapli.com/dashboard/products/allegro?search={sku}")
        page.wait_for_timeout(5000)
        page.screenshot(path="debug_gapli_search.png")

        # Find the product row and click details
        # The row should have the SKU
        try:
            details_link = page.locator(f"tr:has-text('{sku}') a[href*='/dashboard/products/allegro/']").first
            if details_link.is_visible():
                product_url = details_link.get_attribute("href")
                logger.info(f"Navigating to product details: {product_url}")
                page.goto(f"https://gapli.com{product_url}")
                page.wait_for_timeout(5000)
                page.screenshot(path="debug_gapli_details.png")
                
                # Extract any error text
                error_box = page.locator(".alert-danger, .text-danger, .error-message").all_text_contents()
                if error_box:
                    logger.info(f"Found errors in UI: {error_box}")
                
                # Check for "Logs" or "History"
                history_tab = page.locator("a:has-text('Historia'), a:has-text('History'), a:has-text('Logi')").first
                if history_tab.is_visible():
                    history_tab.click()
                    page.wait_for_timeout(3000)
                    page.screenshot(path="debug_gapli_history.png")
            else:
                logger.error("Product link not found in search results.")
        except Exception as e:
            logger.error(f"Error finding details: {e}")

        browser.close()

if __name__ == "__main__":
    view_error()

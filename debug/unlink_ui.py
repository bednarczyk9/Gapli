import os
import sys
import logging
import time

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "archive"))
from keywords.gapli_keywords import start_browser_and_login

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def unlink_product():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    sku = "12014_88"
    account_id = "63" # skarbiec_ofert

    logger.info("Logging in to un-link product...")
    playwright_instance, page, client = start_browser_and_login(username, password)

    if not page:
        logger.error("Failed to login.")
        return

    try:
        url = f"https://gapli.com/dashboard/products?konto_allegro_id={account_id}&search={sku}"
        page.goto(url, wait_until="networkidle")
        time.sleep(4)
        
        # Przewijanie w dół (Scroll down) aby załadować wszystkie produkty (lazy loading)
        logger.info("Scrolling down to load products...")
        for _ in range(5):
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(1.5)
        
        row = page.locator(f"tr:has-text('{sku}')").first
        if row.is_visible():
            # Open Actions Menu
            actions_btn = row.locator("button[aria-haspopup='menu']").first
            if actions_btn.is_visible():
                actions_btn.click()
                time.sleep(2)
                
                # Look for Unlink (Odłącz)
                unlink_btn = page.locator("div[role='menu'] button:has-text('Odłącz')").first
                if unlink_btn.is_visible():
                    unlink_btn.click()
                    logger.info("Clicked Odłącz (Unlink).")
                    time.sleep(2)
                    
                    # Confirm if modal appears
                    confirm_btn = page.locator("button:has-text('Potwierdź'), button:has-text('Tak')").first
                    if confirm_btn.is_visible():
                        confirm_btn.click()
                        logger.info("Confirmed unlinking.")
                        time.sleep(3)
                else:
                    logger.info("Odłącz button not found in actions menu.")
        else:
            logger.error("Product not found in list.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        playwright_instance.stop()

if __name__ == "__main__":
    unlink_product()

import os
import sys
import logging
import time

# Add current and archive directory to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "archive"))

from keywords.gapli_keywords import start_browser_and_login
from libs.product_automation import ProductAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def force_sync_v6():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    sku = "1053851_131"

    logger.info("Starting browser and logging in using official keywords...")
    playwright_instance, page, client = start_browser_and_login(username, password)

    if not page:
        logger.error("Failed to start browser or login.")
        if playwright_instance:
            playwright_instance.stop()
        return

    try:
        automation = ProductAutomation(page, client=client, username=username, password=password)
        
        # We know the product is SKU 1053851_131 on account AlejaOkazji (116)
        # Instead of using the generic automation, let's go directly to the target
        logger.info(f"Navigating to SKU {sku} on AlejaOkazji marketplace...")
        page.goto(f"https://gapli.com/dashboard/products/allegro?konto_allegro_id=116&search={sku}", wait_until="networkidle")
        time.sleep(10)
        
        # Check if we see the product
        row = page.locator(f"tr:has-text('{sku}')").first
        if not row.is_visible():
            # Try to click 'Produkty dodane' tab first
            logger.info("Product not visible in 'All'. Checking 'Sent' tab...")
            sent_tab = page.locator("button:has-text('Produkty dodane')").first
            if sent_tab.is_visible():
                sent_tab.click()
                time.sleep(5)
                row = page.locator(f"tr:has-text('{sku}')").first
        
        if row.is_visible():
            logger.info(f"Found product {sku} in UI.")
            # Take a screenshot to verify what we see
            page.screenshot(path="debug_final_attempt.png")
            
            # Look for the update/sync button
            # In Gapli it's often a button with an icon and a tooltip
            sync_btn = row.locator("button[title*='Aktualizuj'], button[title*='Sync']").first
            if sync_btn.is_visible():
                logger.info("Clicking sync/update button...")
                sync_btn.click()
                time.sleep(10)
                page.screenshot(path="debug_final_after_click.png")
                logger.info("Sync triggered via UI.")
            else:
                logger.warning("Sync button not found. Trying actions menu.")
                actions_btn = row.locator("button[aria-haspopup='menu']").first
                if actions_btn.is_visible():
                    actions_btn.click()
                    time.sleep(2)
                    update_opt = page.locator("div[role='menu'] button:has-text('Aktualizuj')").first
                    if update_opt.is_visible():
                        update_opt.click()
                        logger.info("Clicked Aktualizuj in actions menu.")
                        time.sleep(10)
        else:
            logger.error("Could not find the product in Gapli UI.")
            page.screenshot(path="debug_final_fail.png")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        logger.info("Closing browser...")
        playwright_instance.stop()

if __name__ == "__main__":
    force_sync_v6()

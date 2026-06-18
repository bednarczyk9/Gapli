import time
import os
import logging
from playwright.sync_api import sync_playwright
from libs.gapli_client import GapliClient
from libs.product_automation import ProductAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def force_ui_sync():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    sku = "1053851_131"
    store_name = "AlejaOkazji"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        client = GapliClient(page)
        automation = ProductAutomation(page, client, username, password)
        
        logger.info("Logging into Gapli...")
        if not client.login(username, password):
            logger.error("Login failed.")
            browser.close()
            return

        logger.info(f"Navigating to marketplace for {store_name}...")
        # Custom navigation to ensure we are on the right page
        page.goto(f"https://gapli.com/dashboard/products/allegro?konto_allegro_id=116&search={sku}")
        time.sleep(5)
        
        page.screenshot(path="debug_gapli_search.png")
        
        # Check if product is found
        product_row = page.locator(f"tr:has-text('{sku}')").first
        if not product_row.is_visible():
            logger.error(f"Product {sku} not found on page.")
            browser.close()
            return
            
        logger.info(f"Found product row for {sku}.")
        
        # Look for sync/update button
        # Based on Gapli UI, there might be a 'Sync' icon or a button in 'Akcje'
        
        # Let's look for buttons in that row
        buttons = product_row.locator("button").all()
        logger.info(f"Found {len(buttons)} buttons in the row.")
        
        for i, btn in enumerate(buttons):
            tooltip = btn.get_attribute("title") or ""
            text = btn.inner_text().strip()
            logger.info(f"Button {i}: '{text}' Tooltip: '{tooltip}'")
            
            if "Aktualizuj" in tooltip or "Sync" in tooltip or "Wyślij" in text:
                logger.info(f"Clicking button: {tooltip or text}")
                btn.click()
                time.sleep(3)
                page.screenshot(path="debug_after_sync_click.png")
                logger.info("Sync triggered via UI.")
                break
        else:
            logger.warning("No clear sync button found. Checking for 'Akcje' menu.")
            # Sometimes it's under a '...' menu
            actions_btn = product_row.locator("button[aria-haspopup='menu']").first
            if actions_btn.is_visible():
                actions_btn.click()
                time.sleep(1)
                page.screenshot(path="debug_actions_menu.png")
                # Look for 'Aktualizuj' in menu
                update_opt = page.locator("div[role='menu'] button:has-text('Aktualizuj')").first
                if update_opt.is_visible():
                    update_opt.click()
                    logger.info("Clicked 'Aktualizuj' from actions menu.")
                    time.sleep(3)
                else:
                    logger.warning("Could not find 'Aktualizuj' in menu.")
            
        browser.close()

if __name__ == "__main__":
    force_ui_sync()

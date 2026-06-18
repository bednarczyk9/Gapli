import os
import time
import json
import logging
import subprocess
from playwright.sync_api import sync_playwright

# Update sys.path to include current directory for libraries
import sys
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def discover_delete_endpoint():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")
    
    if not username or not password:
        logger.error("GAPLI_USER or GAPLI_PASS not set.")
        return

    port = 9222
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
    
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    profile_path = os.path.join(os.environ.get("TEMP", "."), "chrome-discovery")
    
    chrome_args = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_path}",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    
    logger.info("Starting Chrome...")
    subprocess.Popen(chrome_args)
    time.sleep(5)
    
    with sync_playwright() as p:
        try:
            from libs.gapli_client import GapliClient
            
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0]
            page = context.new_page()
            
            captured = []
            def on_request(request):
                if "/api/" in request.url:
                     captured.append({
                         "url": request.url,
                         "method": request.method,
                         "data": request.post_data
                     })
            
            page.on("request", on_request)
            
            client = GapliClient(page)
            logger.info("Logging in via GapliClient...")
            if not client.login(username, password):
                logger.error("Login failed.")
                return
            
            # Go to Allegro products
            logger.info("Navigating to Allegro products...")
            # Use account 61 (radosnydzieciak)
            page.goto("https://gapli.com/dashboard/products/allegro?konto_allegro_id=61&status=ENDED", wait_until="networkidle")
            page.wait_for_timeout(5000)
            page.screenshot(path="dashboard_allegro.png")
            
            # Select first few items
            logger.info("Selecting items...")
            # Gapli usually has checkboxes in a table
            page.locator("input[type='checkbox']").first.wait_for(timeout=20000)
            checkboxes = page.locator("input[type='checkbox']").all()
            logger.info(f"Found {len(checkboxes)} checkboxes.")
            
            if len(checkboxes) > 1:
                # Click the "Select All" if possible, or individual ones
                # Let's try individual to trigger the bulk menu
                for i in range(1, min(6, len(checkboxes))):
                    checkboxes[i].click()
                    time.sleep(0.5)
            
            page.screenshot(path="items_selected.png")

            # Find and click bulk actions
            logger.info("Looking for actions button...")
            # Try different common labels
            actions_btn = page.locator("button:has-text('Akcje'), button:has-text('Działania'), button:has-text('Bulk'), button:has-text('Masowe')").first
            if actions_btn.is_visible():
                logger.info(f"Found actions button: {actions_btn.inner_text()}")
                actions_btn.click()
                time.sleep(2)
                page.screenshot(path="actions_menu.png")
                
                # Look for 'Usuń' (Delete) or 'Zakończ' (End)
                delete_opt = page.locator("li:has-text('Usuń'), div:has-text('Usuń'), span:has-text('Usuń'), button:has-text('Usuń')").first
                if delete_opt.is_visible():
                    logger.info("Clicking delete option...")
                    delete_opt.click()
                    time.sleep(2)
                    page.screenshot(path="delete_confirm.png")
                    
                    # Confirm
                    confirm = page.locator("button:has-text('Tak'), button:has-text('Potwierdź'), button:has-text('Usuń'), button:has-text('Confirm')").first
                    if confirm.is_visible():
                        logger.info("Confirming deletion...")
                        confirm.click()
                        time.sleep(10)
                        page.screenshot(path="after_delete.png")
            else:
                logger.warning("Actions button not found.")
            
            logger.info(f"Captured {len(captured)} API requests total.")
            for c in captured:
                if "delete" in c['url'].lower() or c['method'] == "DELETE" or "listing" in c['url'].lower():
                    logger.info(f"POTENTIAL REQ: {c['method']} {c['url']} | DATA: {c['data']}")
            
            browser.close()
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
        finally:
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)

if __name__ == "__main__":
    discover_delete_endpoint()

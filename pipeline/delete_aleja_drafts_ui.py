import os
import time
import logging
import subprocess
from playwright.sync_api import sync_playwright
import sys
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def delete_aleja_drafts_ui():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")
    
    if not username or not password:
        logger.error("GAPLI_USER or GAPLI_PASS not set.")
        return

    port = 9222
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
    
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    profile_path = os.path.join(os.environ.get("TEMP", "."), "chrome-delete")
    
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
            
            client = GapliClient(page)
            logger.info("Logging in...")
            if not client.login(username, password):
                logger.error("Login failed.")
                page.screenshot(path="login_error.png")
                return
            
            # Target URL: AlejaOkazji (ID 116) - DRAFTS
            url = "https://gapli.com/dashboard/products/allegro?konto_allegro_id=116&status=DRAFT"
            logger.info(f"Navigating to {url}...")
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(5000)
            page.screenshot(path="drafts_page.png")
            
            # Check for authorization error message on page
            if page.locator("text=Błąd autoryzacji, autoryzuj konto, Błąd autoryzacji").is_visible():
                logger.error("Authorization error detected on Gapli page.")
                page.screenshot(path="auth_error_detected.png")
                # Maybe we can click 'Autoryzuj'?
                auth_btn = page.locator("button:has-text('Autoryzuj'), a:has-text('Autoryzuj')").first
                if auth_btn.is_visible():
                    logger.info("Auth button found. User needs to re-authorize.")
                return
            
            for cycle in range(10): # Do 10 cycles
                logger.info(f"Cycle {cycle+1} - Checking for items...")
                
                # Wait for checkboxes to be present
                try:
                    page.wait_for_selector("input[type='checkbox']", timeout=10000)
                except:
                    logger.info("No more checkboxes found. Done?")
                    break
                
                # 1. Click "Select All"
                # Usually the first checkbox in the header
                select_all = page.locator("thead input[type='checkbox']").first
                if select_all.is_visible():
                    logger.info("Clicking Select All...")
                    select_all.click()
                    time.sleep(1)
                else:
                    logger.warning("Select All checkbox not found.")
                    break
                
                # 2. Open Actions menu
                actions_btn = page.locator("button:has-text('Działania'), button:has-text('Akcje')").first
                if actions_btn.is_visible():
                    logger.info("Opening Actions menu...")
                    actions_btn.click()
                    time.sleep(1)
                    
                    # 3. Click 'Usuń'
                    delete_opt = page.locator("li:has-text('Usuń'), div:has-text('Usuń'), span:has-text('Usuń'), button:has-text('Usuń')").first
                    if delete_opt.is_visible():
                        logger.info("Clicking delete...")
                        delete_opt.click()
                        time.sleep(1)
                        
                        # 4. Confirm in modal
                        confirm = page.locator("button:has-text('Tak'), button:has-text('Potwierdź'), button:has-text('Usuń')").first
                        if confirm.is_visible():
                            logger.info("Confirming deletion...")
                            confirm.click()
                            logger.info("Waiting for deletion to complete...")
                            time.sleep(15) # Wait for processing
                            page.reload()
                            page.wait_for_load_state("networkidle")
                        else:
                            logger.error("Confirmation button not found.")
                            break
                    else:
                        logger.error("Delete option not found in menu.")
                        break
                else:
                    logger.error("Actions button not found.")
                    break
            
            logger.info("Bulk deletion finished.")
            browser.close()
        except Exception as e:
            logger.error(f"Deletion failed: {e}")
        finally:
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)

if __name__ == "__main__":
    delete_aleja_drafts_ui()

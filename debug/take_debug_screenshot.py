import os
import time
import logging
import subprocess
from playwright.sync_api import sync_playwright
import sys
sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def take_debug_screenshot():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")
    
    port = 9222
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
    
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    profile_path = os.path.join(os.environ.get("TEMP", "."), "chrome-debug")
    
    chrome_args = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_path}",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    
    subprocess.Popen(chrome_args)
    time.sleep(5)
    
    with sync_playwright() as p:
        try:
            from libraries.gapli_client import GapliClient
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0]
            page = context.new_page()
            
            client = GapliClient(page)
            if client.login(username, password):
                # Go to Allegro products
                url = "https://gapli.com/dashboard/marketplace/products?konto_allegro_id=116"
                logger.info(f"Navigating to {url}...")
                page.goto(url, wait_until="load")
                page.wait_for_timeout(15000)
                page.screenshot(path="debug_gapli_drafts.png")
                logger.info("Screenshot saved to debug_gapli_drafts.png")
                
                # Check for table and checkboxes
                content = page.content()
                with open("debug_gapli_drafts.html", "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info("HTML saved to debug_gapli_drafts.html")
            
            browser.close()
        except Exception as e:
            logger.error(f"Failed: {e}")
        finally:
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)

if __name__ == "__main__":
    take_debug_screenshot()

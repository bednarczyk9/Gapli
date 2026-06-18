import os
import time
import json
import logging
import re
from playwright.sync_api import sync_playwright
from keywords.gapli_keywords import start_browser_and_login

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def simulate_add_click():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")
    
    playwright_instance, page, client = start_browser_and_login(username, password)
    if not page:
        logger.error("Failed to login.")
        if playwright_instance: playwright_instance.stop()
        return

    captured_requests = []
    def on_request(request):
        if "/api/" in request.url and request.method == "POST":
            captured_requests.append({
                "method": request.method,
                "url": request.url,
                "post_data": request.post_data,
                "headers": dict(request.headers)
            })
    page.on("request", on_request)

    try:
        logger.info("Navigating to marketplace...")
        page.goto("https://gapli.com/dashboard/marketplace", wait_until="networkidle")
        time.sleep(5)
        
        logger.info(f"Current URL: {page.url}")
        page.screenshot(path="marketplace_debug.png")
        
        # Zaznacz pierwszy produkt
        logger.info("Selecting first product...")
        # Czekaj na wiersze tabeli
        try:
            page.wait_for_selector("input[type='checkbox']", timeout=10000)
            checkbox = page.locator("input[type='checkbox']").nth(1) # skip select all
            checkbox.click(force=True)
            time.sleep(1)
            
            # Kliknij 'Wyślij zaznaczone produkty'
            logger.info("Clicking 'Wyślij zaznaczone produkty'...")
            send_btn = page.get_by_role("button", name="Wyślij zaznaczone produkty")
            send_btn.click(force=True)
            time.sleep(2)
            
            # W modal: Kliknij 'Wyślij na Allegro' (ostatni przycisk)
            logger.info("Clicking 'Wyślij na Allegro'...")
            submit_btn = page.locator("button:visible").filter(has_text=re.compile(r"Wyślij na Allegro|Wyślij produkty", re.I)).last
            submit_btn.click(force=True)
            time.sleep(5)
        except Exception as e:
            logger.warning(f"UI interaction failed: {e}")
            page.screenshot(path="marketplace_fail.png")
        
        print("\nANALIZA PRZECHWYCONEGO RUCHU (UI CLICK):")
        for req in captured_requests:
            print("-" * 40)
            print(f"URL: {req['url']}")
            print(f"DATA: {req['post_data']}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if playwright_instance:
            playwright_instance.stop()

if __name__ == "__main__":
    simulate_add_click()

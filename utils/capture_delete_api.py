import os
import time
import json
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Note: We need the actual user password or an active session. 
# Since I can't ask for the password now, I'll try to find it in the environment or use a saved session if any.
# For now, I'll prepare the script to be ready for execution.

def capture_delete_api():
    sku = "1004260-660_150"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # Headful so user can see or I can debug
        context = browser.new_context()
        page = context.new_page()
        
        captured_requests = []
        def handle_request(request):
            if "/api/" in request.url:
                captured_requests.append({
                    "method": request.method,
                    "url": request.url,
                    "post_data": request.post_data
                })
        
        page.on("request", handle_request)
        
        logger.info("Navigating to Gapli Login...")
        page.goto("https://gapli.com/login")
        
        print("\n!!! PROSZE ZALOGUJ SIE W OKNIE PRZEGLADARKI I KLIKNIJ USUN DLA SKU 1004260-660_150 !!!")
        print("Czekam 60 sekund na Twoją akcję...")
        
        # Wait for user to log in and perform the delete action manually
        # while I capture the network traffic
        time.sleep(60)
        
        print("\nCaptured API calls during your action:")
        for req in captured_requests:
            if "customization" in req["url"].lower() or sku in req["url"]:
                print(f"{req['method']} {req['url']}")
                if req["post_data"]:
                    print(f"  Data: {req['post_data']}")
        
        browser.close()

if __name__ == "__main__":
    capture_delete_api()

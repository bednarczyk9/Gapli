import os
import time
import sys
sys.path.append(os.getcwd())
from playwright.sync_api import sync_playwright

def sync_via_ui():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")
    
    with sync_playwright() as p:
        # Using a normal browser to avoid Turnstile if possible
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print("Logging in...")
        page.goto("https://gapli.com/login")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button:has-text("Zaloguj się")')
        
        try:
            page.wait_for_url("**/dashboard**", timeout=20000)
            print("Login success!")
            
            print("Navigating to integrations...")
            page.goto("https://gapli.com/dashboard/integrations/marketplace")
            page.wait_for_timeout(5000)
            page.screenshot(path="integrations_page.png")
            
            # Look for account 116 (AlejaOkazji)
            # Find the row with AlejaOkazji
            row = page.locator("tr:has-text('AlejaOkazji'), div:has-text('AlejaOkazji')").first
            if row.is_visible():
                print("Found AlejaOkazji row.")
                # Look for 'Synchronizuj' or 'Odśwież' button
                sync_btn = row.locator("button:has-text('Synchronizuj'), button:has-text('Odśwież'), button:has-text('Fix')").first
                if sync_btn.is_visible():
                    print("Clicking Synchronizuj...")
                    sync_btn.click()
                    page.wait_for_timeout(5000)
                    page.screenshot(path="after_sync.png")
                else:
                    print("Sync button not found. Maybe it's a dropdown?")
                    # Try to find 'Manage Limits' button
                    limit_btn = page.locator("button[title*='limit']").first
                    if limit_btn.is_visible():
                        print("Clicking Limit button...")
                        limit_btn.click()
                        page.wait_for_timeout(3000)
                        page.screenshot(path="limit_modal.png")
            else:
                print("AlejaOkazji row not found.")
                
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="ui_sync_error.png")
        
        browser.close()

if __name__ == "__main__":
    sync_via_ui()

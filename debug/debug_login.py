import os
import time
import sys
sys.path.append(os.getcwd())
from playwright.sync_api import sync_playwright

def debug_login():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Navigating to login page...")
        page.goto("https://gapli.com/login")
        time.sleep(2)
        page.screenshot(path="login_start.png")
        
        print("Filling form...")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.screenshot(path="login_filled.png")
        
        print("Clicking login...")
        page.click('button:has-text("Zaloguj się")')
        time.sleep(5)
        
        print(f"URL after login: {page.url}")
        page.screenshot(path="login_after.png")
        
        if "dashboard" in page.url:
            print("Login success!")
        else:
            print("Login failed.")
            # Check for error message
            error = page.locator("div.text-red-300, div.text-red-500, div[class*='error']").first
            if error.is_visible():
                print(f"Error message: {error.inner_text()}")
        
        browser.close()

if __name__ == "__main__":
    debug_login()

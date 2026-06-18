from playwright.sync_api import sync_playwright
import time

def search_allegro_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        seller = "AlejaOkazji"
        url = f"https://allegro.pl/uzytkownik/{seller}"
        print(f"Navigating to {url}")
        page.goto(url)
        time.sleep(5)
        
        page.screenshot(path="debug_aleja_okazji_full.png", full_page=True)
        print(f"Page Title: {page.title()}")
        print(f"Content Length: {len(page.content())}")
        
        # Check if we got hit by CAPTCHA
        if "captcha" in page.content().lower() or "robot" in page.content().lower():
            print("!!! BOT DETECTION DETECTED !!!")
        
        browser.close()

if __name__ == "__main__":
    search_allegro_ui()

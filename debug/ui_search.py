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
        # ...
        page.screenshot(path="debug_aleja_okazji.png")
        
        # Handle cookies
        try:
            page.wait_for_selector('button:has-text("ok, zgadzam się")', timeout=5000)
            page.click('button:has-text("ok, zgadzam się")')
        except: pass
        
        time.sleep(2)
        
        # Check if items found
        items = page.locator('article[data-analytics-view-custom-index0]')
        count = items.count()
        print(f"Found {count} items via UI.")
        
        for i in range(count):
            item = items.nth(i)
            title = item.locator('h2').inner_text()
            link = item.locator('h2 a').get_attribute('href')
            print(f"- {title} ({link[:50]}...)")
            
        browser.close()

if __name__ == "__main__":
    search_allegro_ui()

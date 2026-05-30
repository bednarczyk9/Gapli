from playwright.sync_api import sync_playwright
import time

def find_sync_button():
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            url = "https://gapli.com/dashboard/products/allegro?search=2026_24"
            print(f"Navigating to {url}...")
            page.goto(url, wait_until="networkidle")
            time.sleep(3)
            
            print("Current URL:", page.url)
            
            # Find buttons that might trigger sync
            buttons = page.query_selector_all("button")
            found_buttons = []
            for btn in buttons:
                text = btn.inner_text().strip()
                if text:
                    found_buttons.append(text)
                    if "sync" in text.lower() or "aktualizuj" in text.lower() or "wyślij" in text.lower():
                        print(f"DEBUG: Found relevant button: '{text}'")
            
            print("All buttons:", found_buttons)
            
            # Check for specific sync icon or tooltip
            # Often there is a sync icon next to the status
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    find_sync_button()

from playwright.sync_api import sync_playwright
import time

def list_btns():
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            pg = browser.contexts[0].pages[0]
            print(f"URL: {pg.url}")
            
            # Wait for SKU
            if pg.get_by_text("1053851_131").first.is_visible():
                print("SKU visible.")
                btns = pg.locator("button").all()
                for i, b in enumerate(btns):
                    t = b.inner_text().strip()
                    title = b.get_attribute("title") or ""
                    if t or title:
                         print(f"BTN {i}: '{t}' [{title}]")
                         if "Retry" in t or "Retry" in title or "Wyślij" in t:
                              print(f"--> FOUND! Clicking {i}")
                              b.click()
                              time.sleep(5)
                              print("Clicked.")
                              return
            else:
                print("SKU not visible.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    list_btns()

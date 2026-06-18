from playwright.sync_api import sync_playwright
import time

def find_gapli():
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            ctx = browser.contexts[0]
            print(f"Found {len(ctx.pages)} pages.")
            for i, pg in enumerate(ctx.pages):
                print(f"Page {i}: {pg.url}")
                pg.screenshot(path=f"debug_page_{i}.png")
                
                if "gapli.com" in pg.url:
                    print("GAPLI FOUND!")
                    # Try to find the SKU on this page
                    if pg.get_by_text("1053851_131").first.is_visible():
                        print("SKU FOUND on page!")
                        # List all buttons
                        btns = pg.locator("button").all()
                        for b in btns:
                            txt = b.inner_text().strip()
                            if txt in ["Retry", "Wyślij", "Ponów", "Synchronizuj"]:
                                print(f"Clicking button: {txt}")
                                b.click()
                                time.sleep(5)
                                pg.screenshot(path="debug_final_click_result.png")
                                return
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    find_gapli()

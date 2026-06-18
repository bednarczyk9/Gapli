import os
import sys
import time
import logging
from playwright.sync_api import sync_playwright

sys.path.append(os.getcwd())
try:
    from libs.chrome_manager import ChromeManager
except ImportError:
    logging.error("Could not import ChromeManager. Make sure you run this from the project root.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def check_offer(offer_id):
    chrome = ChromeManager()
    logging.info("Starting Chrome via ChromeManager...")
    if not chrome.start_chrome():
        logging.error("Failed to start Chrome")
        return
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.new_page()
            
            url = f"https://business.allegro.pl/oferta/{offer_id}"
            logging.info(f"Navigating to {url}")
            page.goto(url)
            page.wait_for_timeout(5000) # Give it time to load the React app
            
            # Take screenshot for visual debugging
            screenshot_path = f"debug_allegro_offer_{offer_id}.png"
            page.screenshot(path=screenshot_path)
            logging.info(f"Saved screenshot to {screenshot_path}")
            
            logging.info("Extracting error messages from the page...")
            
            # Look for common Allegro error indicators
            error_keywords = ['wymagane', 'uzupełnij', 'błąd', 'niepoprawn', 'brakuje', 'error', 'invalid']
            
            # Check for general alerts
            alerts = page.locator("[data-role='alert'], .m-message--error, [data-box-name='alert']").all()
            for alert in alerts:
                if alert.is_visible():
                    print("--- ZNALEZIONO KOMUNIKAT BŁĘDU ---")
                    print(alert.inner_text().strip())
                    print("----------------------------------")

            # Scan the whole page text line by line for hints
            page_text = page.locator("body").inner_text()
            print("\n--- ANALIZA TEKSTU STRONY (podejrzane fragmenty) ---")
            lines = [line.strip() for line in page_text.split('\n') if line.strip()]
            for i, line in enumerate(lines):
                if any(kw in line.lower() for kw in error_keywords):
                    # Print context (previous line, current line, next line)
                    ctx_start = max(0, i - 1)
                    ctx_end = min(len(lines), i + 2)
                    print(f"Kontekst [Linie {ctx_start}-{ctx_end}]:")
                    for j in range(ctx_start, ctx_end):
                        prefix = ">>> " if j == i else "    "
                        print(f"{prefix}{lines[j]}")
                    print("-" * 20)
            
            # Specifically check parameters section
            print("\n--- SPRAWDZANIE PARAMETRÓW ---")
            param_labels = page.locator("label").all()
            for label in param_labels:
                if label.is_visible():
                    text = label.inner_text().lower()
                    if any(kw in text for kw in error_keywords):
                        print(f"Podejrzany parametr: {label.inner_text().strip()}")
            
            # Try to fetch XHR validation response if available
            # Note: since the page is already loaded, we might need to trigger a 'save' or just rely on DOM
            # To be safe, we just rely on DOM.
            
            browser.close()
            
            print(f"\nGotowe. Obejrzyj zrzut ekranu {screenshot_path} aby zobaczyć co dokładnie wyświetla Allegro.")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        chrome.kill_chrome()

if __name__ == "__main__":
    offer_id = sys.argv[1] if len(sys.argv) > 1 else "18652435185"
    check_offer(offer_id)

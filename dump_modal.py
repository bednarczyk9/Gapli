from playwright.sync_api import sync_playwright
import sys

def dump_page():
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
            context = browser.contexts[0]
            page = context.pages[0]
            content = page.content()
            with open('page_dump_modal.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully dumped page to page_dump_modal.html")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_page()

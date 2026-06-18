import asyncio
from playwright.async_api import async_playwright

async def inspect_modal():
    async with async_playwright() as p:
        try:
            print("Connecting to Chrome on port 9222...")
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            target_page = None
            for context in browser.contexts:
                for page in context.pages:
                    if "gapli.com" in page.url:
                        target_page = page
                        break
                if target_page:
                    break
            
            if not target_page:
                print("Error: Could not find an open gapli.com tab.")
                return

            print(f"Connected to: {target_page.url}")
            
            # Look for the modal dialog
            dialog = target_page.locator("div[role='dialog'], .modal-content, .fixed.inset-0").first
            
            if await dialog.is_visible():
                print("Found active modal dialog! Extracting HTML...")
                html = await dialog.inner_html()
                print("--- MODAL HTML ---")
                print(html)
                print("------------------")
                
                # Check for inputs
                inputs = dialog.locator("input")
                count = await inputs.count()
                print(f"Found {count} input field(s) in the modal.")
                if count > 0:
                    placeholder = await inputs.first.get_attribute("placeholder")
                    print(f"Input placeholder: {placeholder}")
            else:
                print("No active modal dialog found on the page. Dumping body text instead:")
                print(await target_page.locator("body").inner_text())

        except Exception as e:
            print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_modal())

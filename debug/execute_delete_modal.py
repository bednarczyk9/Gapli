import asyncio
import json
from playwright.async_api import async_playwright

async def execute_delete():
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
            
            def handle_request(request):
                if "api/" in request.url and request.method in ["DELETE", "POST", "PUT", "PATCH"]:
                    print(f"--- INTERCEPTED API CALL ---")
                    print(f"Method: {request.method}")
                    print(f"URL: {request.url}")
                    print(f"Data: {request.post_data}")
                    print(f"----------------------------")
            
            target_page.on("request", handle_request)
            
            dialog = target_page.locator("div[role='dialog'], .modal-content, .fixed.inset-0").first
            
            if await dialog.is_visible():
                print("Found active modal dialog!")
                
                # Check input, fill 1 just in case
                inputs = dialog.locator("input")
                if await inputs.count() > 0:
                    await inputs.first.fill("1")
                    await target_page.wait_for_timeout(500)
                
                # Click the delete button
                del_btn = dialog.locator("button.bg-red-700, button:has-text('Usuń permanentnie')").last
                if await del_btn.is_visible() and await del_btn.is_enabled():
                    print("Clicking Delete button...")
                    await del_btn.click()
                    await target_page.wait_for_timeout(3000) # Wait for network
                else:
                    print("Delete button not enabled or visible.")
            else:
                print("No active modal dialog found.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(execute_delete())

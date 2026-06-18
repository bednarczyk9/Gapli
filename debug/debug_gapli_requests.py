import asyncio
from playwright.async_api import async_playwright
import re

async def debug_gapli():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            
            target_page = None
            for page in context.pages:
                if "gapli.com" in page.url:
                    target_page = page
                    break
            
            if not target_page:
                print("Gapli page not found in the browser.")
                return

            print(f"Connected to page: {target_page.url}")
            
            # Listen for requests
            async def handle_request(request):
                if "gapli.com/api" in request.url:
                    try:
                        response = await request.response()
                        if response and response.status == 403:
                            print(f"403 Forbidden Detected: {request.url}")
                            print(f"  Request Headers: {request.headers}")
                            # Try to get response text
                            try:
                                text = await response.text()
                                print(f"  Response Body: {text[:200]}...")
                            except: pass
                    except: pass

            target_page.on("requestfinished", handle_request)
            
            print("Reloading page to capture 403 details...")
            await target_page.reload()
            await target_page.wait_for_timeout(10000)
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_gapli())

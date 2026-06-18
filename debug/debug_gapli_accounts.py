import asyncio
from playwright.async_api import async_playwright
import re
import json

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
                print("Gapli page not found.")
                return

            print(f"Connected to page: {target_page.url}")
            
            # Fetch markets to see what market 7 is
            token = await target_page.evaluate("localStorage.getItem('authToken')")
            if token:
                endpoint = "/api/products-manager/markets"
                api_result = await target_page.evaluate(f"""
                    async (token) => {{
                        const response = await fetch('{endpoint}', {{
                            headers: {{ 'Authorization': 'Bearer ' + token }}
                        }});
                        return await response.json();
                    }}, '{token}'
                """)
                print(f"Markets: {json.dumps(api_result, indent=2)}")
            else:
                print("No token found.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_gapli())

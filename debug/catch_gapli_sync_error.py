import asyncio
from playwright.async_api import async_playwright
import os
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def catch_error():
    username = os.environ.get("GAPLI_USER")
    password = os.environ.get("GAPLI_PASS")
    sku = "12014_88"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Monitor responses
        async def handle_response(response):
            if "integrations/marketplace/listing" in response.url or "sync-logs" in response.url or "operation-history" in response.url:
                try:
                    text = await response.text()
                    logger.info(f"CAPTURED RESPONSE from {response.url}: {text[:500]}...")
                except:
                    pass

        page.on("response", handle_response)

        logger.info("Logging in...")
        await page.goto("https://gapli.com/login")
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="password"]', password)
        await page.click('button:has-text("Zaloguj się")')
        await page.wait_for_url("**/dashboard**")

        logger.info(f"Searching for SKU {sku}...")
        await page.goto(f"https://gapli.com/dashboard/products/allegro?search={sku}")
        await page.wait_for_timeout(5000)

        # Click Retry button if visible in the list
        retry_btn = page.locator("button:has-text('Retry'), button:has-text('Ponów')").first
        if await retry_btn.is_visible():
            logger.info("Found Retry button. Clicking...")
            await retry_btn.click()
            await page.wait_for_timeout(10000)
        else:
            logger.error("Retry button not found in list. Trying details page...")
            details_link = page.locator(f"tr:has-text('{sku}') a[href*='/dashboard/products/allegro/']").first
            if await details_link.is_visible():
                product_url = await details_link.get_attribute("href")
                await page.goto(f"https://gapli.com{product_url}")
                await page.wait_for_timeout(5000)
                
                # Look for Retry in details
                retry_btn = page.locator("button:has-text('Retry'), button:has-text('Ponów')").first
                if await retry_btn.is_visible():
                    logger.info("Found Retry button in details. Clicking...")
                    await retry_btn.click()
                    await page.wait_for_timeout(10000)
                else:
                    logger.error("Retry button still not found.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(catch_error())

import logging
from playwright.sync_api import sync_playwright
from libraries.chrome_manager import ChromeManager
from libraries.gapli_client import GapliClient
from libraries.product_automation import ProductAutomation
from libraries.excel_reader import ExcelReader

def start_browser_and_login(username, password):
    """Starts Chrome and logs into Gapli."""
    chrome = ChromeManager()
    if not chrome.start_chrome():
        return None, None

    p = sync_playwright().start()
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    client = GapliClient(page)
    if not client.login(username, password):
        return p, None

    # Zmniejszenie zoomu do 50% po zalogowaniu
    client.set_zoom(50)

    return p, page

def process_store_products(page, store_name, wholesalers_file, config):
    """Main workflow to process products for a specific store."""
    automation = ProductAutomation(page)
    reader = ExcelReader(wholesalers_file)
    wholesalers = reader.read_wholesalers()

    if not wholesalers:
        logging.error("No wholesalers to process.")
        return

    if not automation.select_store(store_name):
        return

    if not automation.navigate_to_marketplace():
        return

    automation.set_basic_filters(config['min_price_filter'], config['min_stock'])

    for wholesaler in wholesalers:
        logging.info(f"Processing wholesaler: {wholesaler}")
        if not automation.select_wholesaler(wholesaler):
            continue

        max_pages = automation.get_max_pages()
        max_safety_limit = 500
        
        pages_to_process = min(max_pages, max_safety_limit)
        logging.info(f"Wholesaler {wholesaler} has {max_pages} pages. Processing up to {pages_to_process}.")

        for page_num in range(1, pages_to_process + 1):
            if not automation.process_page(
                page_num, 
                store_name, 
                config['min_price_final'], 
                config['max_price_final']
            ):
                logging.info(f"Stopping processing for {wholesaler} at page {page_num}.")
                break

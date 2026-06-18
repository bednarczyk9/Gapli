import logging
import os
import sys

# Dodanie katalogu głównego projektu do sys.path, aby umożliwić importy z 'libs'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from playwright.sync_api import sync_playwright
from libs.chrome_manager import ChromeManager
from libs.gapli_client import GapliClient
from libs.product_automation import ProductAutomation
from libs.excel_reader import ExcelReader

def start_browser_and_login(username, password):
    """Starts Chrome and logs into Gapli."""
    # Standard User Agent to avoid detection
    # ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    chrome = ChromeManager()#user_agent=ua
    if not chrome.start_chrome():
        return None, None, None

    p = sync_playwright().start()
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    client = GapliClient(page)
    if not client.login(username, password):
        return p, None, None

    # Zmniejszenie zoomu do 50% po zalogowaniu
    # client.set_zoom(50)

    return p, page, client

def process_store_products(page, store_name, wholesalers_file, config, client=None, username=None, password=None):
    """Main workflow to process products for a specific store."""
    automation = ProductAutomation(page, client=client, username=username, password=password)
    reader = ExcelReader(wholesalers_file)
    wholesalers = reader.read_wholesalers()

    if not wholesalers:
        logging.error("No wholesalers to process.")
        return "No Wholesalers"

    logging.info(f"Selecting store: {store_name}")
    if not automation.select_store(store_name):
        return "Failed Store Selection"

    logging.info("Navigating to marketplace...")
    if not automation.navigate_to_marketplace():
        return "Failed Marketplace Navigation"

    automation.set_basic_filters(
        config['min_price_filter'], 
        config.get('max_price_filter', config['max_price_final']), 
        config['min_stock'],
        store_name=store_name
    )

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

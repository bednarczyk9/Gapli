import os
import logging
from keywords.gapli_keywords import start_browser_and_login, process_store_products

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configuration
STORES = ["hit_bazar", "radosnydzieciak", "skarbiec_ofert"]
WHOLESALERS_FILE = "Recorded/hurtownie_allegro.xlsx"

CONFIG = {
    'min_price_filter': 200,
    'min_stock': 2,
    'min_price_final': 200,
    'max_price_final': 44000
}

def main():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")

    if not username or not password:
        logging.error("GAPLI_USER or GAPLI_PASS environment variables not set.")
        return

    playwright_instance, page = start_browser_and_login(username, password)

    if not page:
        logging.error("Failed to start browser or login.")
        if playwright_instance:
            playwright_instance.stop()
        return

    try:
        for store_name in STORES:
            logging.info(f"Starting process for store: {store_name}")
            result = process_store_products(page, store_name, WHOLESALERS_FILE, CONFIG)
            logging.info(f"Finished process for store: {store_name} with result: {result}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        logging.info("Closing browser...")
        playwright_instance.stop()

if __name__ == "__main__":
    main()

import os
import logging
from keywords.gapli_keywords import start_browser_and_login, process_store_products
from robocorp.tasks import task


# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configuration
STORES = ["hit_bazar", "radosnydzieciak", "skarbiec_ofert"]
# STORES = ["radosnydzieciak"]
WHOLESALERS_FILE = "Recorded/hurtownie_allegro.xlsx"

CONFIG = {
    'min_price_filter': 80,
    'max_price_filter': 50000,
    'min_stock': 2,
    'min_price_final': 80,
    'max_price_final': 50000
}

@task
def main():
    username = os.getenv("GAPLI_USER")
    password = os.getenv("GAPLI_PASS")

    if not username or not password:
        logging.error("GAPLI_USER or GAPLI_PASS environment variables not set.")
        return

    while True:
        playwright_instance, page, client = start_browser_and_login(username, password)

        if not page:
            logging.error("Failed to start browser or login. Retrying in 20 seconds...")
            if playwright_instance:
                playwright_instance.stop()
            time.sleep(20)
            continue

        try:
            for store_name in STORES:
                logging.info(f"Starting process for store: {store_name}")
                result = process_store_products(
                    page, 
                    store_name, 
                    WHOLESALERS_FILE, 
                    CONFIG, 
                    client=client, 
                    username=username, 
                    password=password
                )
                logging.info(f"Finished process for store: {store_name} with result: {result}")
            # If we finish all stores successfully, break the loop
            break
        except Exception as e:
            if "RESTART_REQUIRED" in str(e):
                logging.warning("Restart requested by automation logic. Closing browser and waiting 20s...")
            else:
                logging.error(f"An unexpected error occurred: {e}")
        finally:
            logging.info("Closing browser...")
            playwright_instance.stop()
        
        logging.info("Waiting 20 seconds before restart...")
        import time
        time.sleep(20)

if __name__ == "__main__":
    main()

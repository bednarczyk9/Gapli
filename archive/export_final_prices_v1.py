import requests
import json
import pandas as pd
import logging
import time
import os
from datetime import datetime

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mandatory Gapli API Key for V1 Integrations
API_KEY = os.environ.get("Gapli_Apikey")
if not API_KEY:
    # Fallback for local testing if env is not loaded in this shell
    API_KEY = "gapli_69_889988_009900" # Placeholder, actual key is in env

TARGET_COUNT = 100

def get_wholesalers_map():
    """Fetches wholesaler mapping (parser_id -> display_name)."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    # Using v1 endpoint for consistency
    url = "https://gapli.com/api/v1/integrations/wholesalers"
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            wholesalers = resp.json().get("wholesalers", [])
            return {int(w["parser_id"]): w["name"] for w in wholesalers if "parser_id" in w}
        else:
            logger.error(f"Failed to fetch wholesalers: {resp.status_code}")
    except Exception as e:
        logger.error(f"Error fetching wholesalers: {e}")
    return {}

def fetch_products_v1():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    wholesaler_map = get_wholesalers_map()
    all_products = []
    limit = 50
    offset = 0
    
    logger.info(f"Fetching {TARGET_COUNT} products from Integrations Marketplace API...")
    
    while len(all_products) < TARGET_COUNT:
        url = "https://gapli.com/api/v1/integrations/marketplace/products"
        params = {
            "status": "active",
            "limit": limit,
            "offset": offset,
            "platform": "allegro"
        }
        
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=60)
            if resp.status_code != 200:
                logger.error(f"Error: {resp.status_code} {resp.text}")
                break
                
            data = resp.json()
            products = data.get("products", [])
            
            if not products:
                logger.info("No more products found.")
                break
                
            # Enrichment: Get wholesaler name from SKU suffix or product details if available
            # In V1 Marketplace API, wholesaler name is often not directly in the list
            # But we have parser_id in the SKU usually (e.g. 12345_152 -> 152)
            
            for p in products:
                sku = p.get("sku", "")
                parser_id = None
                if "_" in sku:
                    try:
                        parser_id = int(sku.split("_")[-1])
                    except:
                        pass
                
                wholesaler = wholesaler_map.get(parser_id, f"ID: {parser_id}" if parser_id else "Unknown")
                
                # IMPORTANT: In V1, 'price' is the display price in Gapli Marketplace
                p['final_price_gapli'] = p.get('price')
                p['wholesaler_name'] = wholesaler
                
            all_products.extend(products)
            logger.info(f"Fetched {len(all_products)} products so far...")
            
            if not data.get("pagination", {}).get("has_more"):
                break
                
            offset += limit
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            break
            
    return all_products[:TARGET_COUNT]

def run():
    products = fetch_products_v1()
    
    if not products:
        logger.error("No products to save.")
        return
        
    processed = []
    for p in products:
        processed.append({
            "SKU": p.get("sku"),
            "EAN": p.get("ean") or "BRAK", # EAN is crucial for Allegro search
            "Nazwa Produktu": p.get("name"),
            "Cena w Gapli": p.get("final_price_gapli"),
            "Sklep": p.get("store_name") or p.get("allegro_login"),
            "Hurtownia": p.get("wholesaler_name"),
            "Allegro ID": p.get("allegro_offer_id")
        })
    
    df = pd.DataFrame(processed)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gapli_export_v1_prices_{timestamp}.xlsx"
    
    logger.info(f"Saving to {filename}...")
    df.to_excel(filename, index=False)
    logger.info("Export completed successfully!")
    print(f"\nZapisano {len(processed)} produktów do pliku: {filename}")

if __name__ == "__main__":
    run()

import requests
import pandas as pd
import os
import logging
from datetime import datetime

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Token from environment or fallback (for local dev)
TOKEN = os.environ.get("GAPLI_TOKEN", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE")
TARGET_COUNT = 100

def get_wholesalers_map():
    headers = {"Authorization": TOKEN}
    url = "https://gapli.com/api/products-manager/wholesalers"
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            wholesalers = resp.json().get("wholesalers", [])
            return {w["assigned_parser_id"]: w["display_name"] for w in wholesalers if "assigned_parser_id" in w}
        else:
            logger.error(f"Failed to fetch wholesalers: {resp.status_code}")
    except Exception as e:
        logger.error(f"Error fetching wholesalers: {e}")
    return {}

def fetch_products_for_export():
    headers = {
        "Authorization": TOKEN,
        "Accept": "application/json"
    }
    
    wholesaler_map = get_wholesalers_map()
    all_products = []
    limit = 50
    page_num = 1
    
    logger.info(f"Fetching up to {TARGET_COUNT} active products for price analysis export...")
    
    while len(all_products) < TARGET_COUNT:
        # We fetch from the main products-manager endpoint
        url = "https://gapli.com/api/products-manager/allegro/products"
        params = {
            "allegro_offer_status": "active",
            "limit": limit,
            "page": page_num,
            "mode": "full"
        }
        
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=60)
            if resp.status_code != 200:
                logger.error(f"Error: {resp.status_code} {resp.text}")
                break
                
            data = resp.json()
            products = data.get("products", [])
            
            if not products:
                break
                
            all_products.extend(products)
            logger.info(f"Fetched {len(all_products)} products so far...")
            
            if len(products) < limit:
                break
                
            page_num += 1
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            break
            
    # Trim to TARGET_COUNT
    all_products = all_products[:TARGET_COUNT]
    
    processed_data = []
    for p in all_products:
        sku = p.get("sku")
        ean = p.get("gapli_product_global_unique_id") or p.get("gapli_product_manufacturer_code") or "BRAK"
        
        # Prices
        # Use gapli_product_sale_price_brutto as the "Final Price" seen in Gapli UI
        final_price = p.get("gapli_product_sale_price_brutto")
        allegro_price = p.get("allegro_offer_price_final_brutto")
        
        # Wholesaler
        parser_id = p.get("parser_id")
        wholesaler_name = wholesaler_map.get(parser_id, f"ID: {parser_id}")
        
        # Store
        store_name = p.get("store_name") or p.get("allegro_login") or "Unknown"
        
        processed_data.append({
            "SKU": sku,
            "EAN": ean,
            "Nazwa Produktu": p.get("gapli_product_name") or p.get("allegro_catalog_product_name"),
            "Finalna Cena Gapli (Brutto)": final_price,
            "Cena Wysłana na Allegro": allegro_price,
            "Sklep": store_name,
            "Hurtownia": wholesaler_name,
            "Allegro ID": p.get("allegro_offer_id")
        })
        
    return processed_data

def run():
    products = fetch_products_for_export()
    
    if not products:
        logger.error("No products to save.")
        return
        
    df = pd.DataFrame(products)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gapli_final_prices_final_{timestamp}.xlsx"
    
    logger.info(f"Saving {len(products)} products to {filename}...")
    df.to_excel(filename, index=False)
    logger.info("Export completed successfully!")
    print(f"\nZapisano {len(products)} produktów do pliku: {filename}")
    return filename

if __name__ == "__main__":
    run()

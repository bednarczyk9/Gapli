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

# Use token from environment if available, otherwise fallback to known working token
TOKEN = os.environ.get("GAPLI_TOKEN") or "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
TARGET_COUNT = 100

def get_wholesalers_map():
    """Fetches wholesaler mapping (parser_id -> display_name)."""
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
    limit = 100
    page_num = 1
    
    logger.info(f"Fetching {TARGET_COUNT} products for price analysis export...")
    
    # We'll fetch from all accounts or just a specific one? 
    # The user asked for "nazwa sklepu", so fetching from the general products-manager endpoint (without specific account_id) might be better if we want products across all stores.
    # However, 'products-manager/allegro/products' is what we know works for 'mode=full'.
    
    # Let's use account_id=61 as a base, or loop through accounts.
    # For now, let's fetch from the general endpoint if possible, or just account 61 if it's the primary.
    url = f"https://gapli.com/api/products-manager/allegro/products?allegro_offer_status=active&limit={limit}&page={page_num}&mode=full"
    
    try:
        resp = requests.get(url, headers=headers, timeout=60)
        if resp.status_code != 200:
            logger.error(f"Error: {resp.status_code} {resp.text}")
            return []
            
        data = resp.json()
        products = data.get("products", [])
        all_products.extend(products)
        
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return []
            
    # Trim to TARGET_COUNT
    all_products = all_products[:TARGET_COUNT]
    
    processed_data = []
    for p in all_products:
        sku = p.get("sku")
        ean = p.get("gapli_product_global_unique_id")
        
        # Prices
        # Use gapli_product_sale_price_brutto as the "Final Price" seen in Gapli UI
        final_price = p.get("gapli_product_sale_price_brutto")
        
        # If we want to see what is actually on Allegro, we can keep the other one too
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
    filename = f"gapli_final_prices_export_{timestamp}.xlsx"
    
    logger.info(f"Saving {len(products)} products to {filename}...")
    df.to_excel(filename, index=False)
    logger.info("Export completed successfully!")
    print(f"\nZapisano dane do pliku: {filename}")

if __name__ == "__main__":
    run()

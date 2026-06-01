import requests
import json
import pandas as pd
import logging
import time
from datetime import datetime

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
ACCOUNT_ID = "61" # radosnydzieciak
TARGET_COUNT = 1000

def format_parameters(params):
    if not params:
        return ""
    if isinstance(params, list):
        formatted = []
        for p in params:
            name = p.get("name", "Unknown")
            values = p.get("valuesLabels", [])
            if not values and p.get("values"):
                values = p.get("values")
            val_str = ", ".join(map(str, values))
            unit = p.get("unit")
            if unit:
                val_str = f"{val_str} {unit}"
            formatted.append(f"{name}: {val_str}")
        return " | ".join(formatted)
    return str(params)

def format_description(desc_obj):
    if not desc_obj:
        return ""
    if isinstance(desc_obj, str):
        return desc_obj
    # Handle the structure of Allegro section-based description
    if isinstance(desc_obj, dict) and "sections" in desc_obj:
        text_parts = []
        for section in desc_obj.get("sections", []):
            for item in section.get("items", []):
                if item.get("type") == "TEXT":
                    text_parts.append(item.get("content", ""))
        return "\n".join(text_parts)
    return str(desc_obj)

def fetch_products():
    headers = {
        "Authorization": TOKEN,
        "Accept": "application/json"
    }
    
    all_results = []
    limit = 100
    page = 1
    
    logger.info(f"Starting to fetch {TARGET_COUNT} active products for account {ACCOUNT_ID}...")
    
    while len(all_results) < TARGET_COUNT:
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&status=ACTIVE&limit={limit}&page={page}"
        logger.info(f"Fetching page {page}...")
        resp = requests.get(url, headers=headers)
        
        if resp.status_code != 200:
            logger.error(f"Error fetching products: {resp.status_code} {resp.text}")
            break
            
        data = resp.json()
        products = data.get("products", [])
        if not products:
            logger.info("No more products found.")
            break
            
        for p in products:
            # Clean up and rename fields for clarity
            row = {
                'sku': p.get('sku'),
                'name': p.get('gapli_product_name'),
                'price_brutto': p.get('gapli_product_sale_price_brutto'),
                'allegro_offer_id': p.get('allegro_offer_id'),
                'stock_quantity': p.get('gapli_product_stock_quantity'),
                'ean': p.get('gapli_product_global_unique_id') or p.get('ean'),
                'formatted_parameters': format_parameters(p.get("allegro_catalog_parameters")),
                'full_description': format_description(p.get("allegro_catalog_description")),
                'wholesaler': p.get('wholesaler_name')
            }
            all_results.append(row)
            if len(all_results) >= TARGET_COUNT:
                break
            
        logger.info(f"Fetched {len(all_results)} products so far...")
        
        total_pages = data.get("total_pages")
        if total_pages is None:
             # Fallback if total_pages is not provided correctly
             total = data.get("total", 0)
             total_pages = (total + limit - 1) // limit
             
        if page >= total_pages:
            break
            
        page += 1
        time.sleep(0.05)

    # Save to Excel
    df = pd.DataFrame(all_results)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"radosnydzieciak_active_products_{len(all_results)}_{timestamp}.xlsx"
    df_save_path = filename
    df.to_excel(df_save_path, index=False)
    logger.info(f"Successfully saved {len(all_results)} products to {filename}")
    return filename

if __name__ == "__main__":
    fetch_products()

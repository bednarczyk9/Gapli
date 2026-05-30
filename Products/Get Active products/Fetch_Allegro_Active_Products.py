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
    if not params or not isinstance(params, list):
        return ""
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

def format_description(desc_obj):
    if not desc_obj:
        return ""
    if isinstance(desc_obj, str):
        return desc_obj
    
    # If it's the Allegro sections format
    sections = desc_obj.get("sections", [])
    text_parts = []
    for section in sections:
        items = section.get("items", [])
        for item in items:
            if item.get("type") == "TEXT":
                text_parts.append(item.get("content", ""))
    return "\n".join(text_parts)

def fetch_all_active_products():
    headers = {
        "Authorization": TOKEN,
        "Accept": "application/json"
    }
    
    all_products = []
    limit = 100
    page_num = 1
    
    logger.info(f"Starting fetch for {TARGET_COUNT} active products for 'radosnydzieciak' (ID: {ACCOUNT_ID})...")
    
    while len(all_products) < TARGET_COUNT:
        url = f"https://gapli.com/api/products-manager/allegro/products?account_id={ACCOUNT_ID}&allegro_offer_status=active&limit={limit}&page={page_num}&mode=full"
        logger.info(f"Fetching page {page_num}...")
        
        try:
            resp = requests.get(url, headers=headers, timeout=60)
            if resp.status_code != 200:
                logger.error(f"Error: {resp.status_code} {resp.text}")
                break
                
            data = resp.json()
            products = data.get("products", [])
            
            if not products:
                logger.info("No more active products found.")
                break
                
            all_products.extend(products)
            logger.info(f"Total products fetched: {len(all_products)}")
            
            total_pages = data.get("total_pages", 0)
            if page_num >= total_pages:
                break
                
            page_num += 1
            time.sleep(0.5) # Politeness
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            break
            
    # Trim to exactly TARGET_COUNT if we got more
    all_products = all_products[:TARGET_COUNT]
    
    processed_data = []
    for p in all_products:
        # Extract Allegro description (prioritize offer, then catalog)
        desc_allegro_raw = p.get("allegro_offer_description")
        if desc_allegro_raw:
            opis_allegro = format_description(desc_allegro_raw)
        else:
            opis_allegro = format_description(p.get("allegro_catalog_description"))
            
        # Extract Gapli description
        opis_gapli = p.get("gapli_product_description") or ""
        
        params = format_parameters(p.get("allegro_catalog_parameters"))
        
        processed_data.append({
            "Sklep Allegro": p.get("allegro_login") or "radosnydzieciak",
            "SKU": p.get("sku"),
            "Nazwa": p.get("gapli_product_name") or p.get("allegro_catalog_product_name"),
            "Allegro ID": p.get("allegro_offer_id"),
            "Cena Allegro Brutto": p.get("allegro_offer_price_final_brutto") or p.get("gapli_product_sale_price_brutto"),
            "Stan Magazynowy": p.get("gapli_product_stock_quantity"),
            "EAN": p.get("gapli_product_global_unique_id"),
            "Opis Allegro": opis_allegro,
            "Opis Gapli": opis_gapli,
                "Parametry": params,
                "Link Allegro": p.get("allegro_offer_url")
            })
        
    return processed_data

def run():
    products = fetch_all_active_products()
    
    if not products:
        logger.error("No products to save.")
        return
        
    df = pd.DataFrame(products)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"radosnydzieciak_active_products_{len(products)}_{timestamp}.xlsx"
    
    logger.info(f"Saving to {filename}...")
    df.to_excel(filename, index=False)
    logger.info("Success!")
    print(f"\nZapisano {len(products)} produktów do pliku: {filename}")

if __name__ == "__main__":
    run()

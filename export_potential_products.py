import requests
import pandas as pd
import os
import logging
from datetime import datetime

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gapli Token
TOKEN = os.environ.get("GAPLI_TOKEN", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE")
TARGET_COUNT = 100 # Adjust as needed

def fetch_potential_candidates():
    headers = {
        "Authorization": TOKEN,
        "Accept": "application/json"
    }
    
    all_candidates = []
    limit = 50
    page_num = 1
    
    logger.info(f"Searching for up to {TARGET_COUNT} product candidates (in stock, with EAN, not blocked)...")
    
    while len(all_candidates) < TARGET_COUNT:
        url = "https://gapli.com/api/products-manager/products"
        params = {
            "limit": limit,
            "page": page_num
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
                
            for p in products:
                ean = p.get("global_unique_id")
                blocked = p.get("allegro_blocked")
                stock = int(float(p.get("stock_quantity", 0)))
                
                # Filters
                if ean and not blocked and stock > 0:
                    # Calculate Gross Price
                    try:
                        net_price = float(p.get("sale_net_price", 0))
                        tax = int(p.get("tax_class", "23"))
                        gross_price = round(net_price * (1 + tax/100), 2)
                    except:
                        gross_price = 0
                        
                    all_candidates.append({
                        "SKU": p.get("sku"),
                        "EAN": ean,
                        "Nazwa Produktu": p.get("name"),
                        "Cena Brutto (Gapli)": gross_price,
                        "Hurtownia": p.get("wholesaler_name") or "Unknown",
                        "Stan": stock
                    })
                    
                    if len(all_candidates) >= TARGET_COUNT:
                        break
            
            logger.info(f"Checked page {page_num}, found {len(all_candidates)} candidates so far...")
            page_num += 1
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            break
            
    return all_candidates

def run():
    candidates = fetch_potential_candidates()
    
    if not candidates:
        logger.error("No candidates found.")
        return
        
    df = pd.DataFrame(candidates)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gapli_potential_products_{timestamp}.xlsx"
    
    logger.info(f"Saving {len(candidates)} candidates to {filename}...")
    df.to_excel(filename, index=False)
    logger.info("Export completed successfully!")
    print(f"\nZapisano {len(candidates)} potencjalnych produktów do pliku: {filename}")
    return filename

if __name__ == "__main__":
    run()

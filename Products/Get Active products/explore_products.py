import os
import requests
import json
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def explore_more_products():
    api_key = os.environ.get("Gapli_Apikey")
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    
    # Pobierz 10 produktów
    resp = requests.get("https://gapli.com/api/v1/integrations/products?limit=10", headers=headers)
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        for p in products:
            logger.info(f"Produkt: {p['sku']} - {p['name']}")
            # Szukamy czy jest coś jeszcze
            other_keys = [k for k in p.keys() if k not in ['sku', 'name', 'description', 'short_description', 'ean', 'type', 'price_net', 'price_gross', 'wholesale_net_price', 'stock_quantity', 'available', 'weight', 'width', 'height', 'depth', 'is_oversized', 'brand', 'manufacturer_code', 'image_url', 'gallery_images', 'category_ids', 'parser_id', 'tax_class', 'product_condition', 'updated_at', 'sellable']]
            if other_keys:
                logger.info(f"Dodatkowe klucze: {other_keys}")

if __name__ == "__main__":
    explore_more_products()

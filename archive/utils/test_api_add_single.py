import os
import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_add_single_product():
    api_key = os.environ.get("Gapli_Apikey")
    if not api_key:
        logger.error("Gapli_Apikey not found!")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 1. Fetch products from 4KOM (parser_id 34)
    logger.info("Fetching products from 4KOM...")
    url_products = "https://gapli.com/api/v1/integrations/products"
    params = {
        "parser_id": 34,
        "price_gross_min": 60,
        "stock_min": 5,
        "limit": 5
    }
    
    resp = requests.get(url_products, headers=headers, params=params)
    if resp.status_code != 200:
        logger.error(f"Failed to fetch products: {resp.status_code} {resp.text}")
        return
    
    products = resp.json().get("products", [])
    if not products:
        logger.error("No products found for 4KOM.")
        return
    
    # Pick the first one
    product = products[0]
    sku = product["sku"]
    logger.info(f"Picked product: {product['name']} (SKU: {sku})")
    
    # 2. Try to send to AlejaOkazji (ID 116)
    logger.info(f"Attempting to send SKU {sku} to account 116...")
    url_send = "https://gapli.com/api/v1/integrations/marketplace/listing"
    body = {
        "action": "send",
        "account_id": "116",
        "product_skus": [sku],
        "price_range": {
            "min": 60,
            "max": 50000
        }
    }
    
    resp_send = requests.post(url_send, headers=headers, json=body)
    logger.info(f"Response status: {resp_send.status_code}")
    logger.info(f"Response body: {resp_send.text}")

if __name__ == "__main__":
    test_add_single_product()

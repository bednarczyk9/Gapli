import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
ACCOUNT_ID = "61"

def test_filtered_products():
    headers = {
        "Authorization": TOKEN,
        "Accept": "application/json"
    }
    
    # Try filtering by account_id in the main products endpoint
    url = f"https://gapli.com/api/products-manager/products?account_id={ACCOUNT_ID}&limit=5&mode=full"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        products = data.get("products", [])
        logger.info(f"Found {len(products)} products with account_id={ACCOUNT_ID}")
        if products:
            logger.info(f"Sample product SKU: {products[0].get('sku')}")
            logger.info(f"Has description: {'description' in products[0]}")
    else:
        logger.error(f"Error {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    test_filtered_products()

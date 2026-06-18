import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json", "Accept": "application/json"}

def permanent_delete(sku):
    logger.info(f"Looking up all instances of SKU: {sku}")
    
    url = f"https://gapli.com/api/products-manager/allegro/products?search={sku}&mode=full"
    resp = requests.get(url, headers=HEADERS)
    
    if resp.status_code != 200:
        logger.error(f"Failed to fetch products: {resp.status_code}")
        return
        
    products = resp.json().get('products', [])
    if not products:
        logger.info("No products found matching this SKU.")
        return
        
    product_ids = []
    for p in products:
        p_id = p.get('id')
        acc_id = p.get('konto_allegro_id')
        store = p.get('store_name')
        logger.info(f"Found product ID: {p_id} on account: {acc_id} ({store})")
        product_ids.append({
            "id": str(p_id),
            "konto_allegro_id": str(acc_id)
        })
        
    if product_ids:
        logger.info(f"Initiating permanent delete for {len(product_ids)} items...")
        delete_payload = {
            "mode": "selected",
            "product_ids": product_ids
        }
        
        del_url = "https://gapli.com/api/products-manager/allegro/permanent-delete"
        del_resp = requests.delete(del_url, headers=HEADERS, json=delete_payload)
        
        logger.info(f"Delete Response ({del_resp.status_code}): {del_resp.text}")
    else:
        logger.info("No valid product IDs extracted.")

if __name__ == "__main__":
    permanent_delete("AGDADLWYC0009_33")

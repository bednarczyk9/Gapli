import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
ACCOUNT_ID = 63

def list_customized_products():
    url = f"https://gapli.com/api/products-manager/allegro/products"
    params = {
        "konto_allegro_id": ACCOUNT_ID,
        "limit": 100,
        "page": 1,
        "mode": "full"
    }
    
    customized = []
    
    while True:
        logger.info(f"Checking page {params['page']}...")
        resp = requests.get(url, headers=GAPLI_HEADERS, params=params)
        if resp.status_code != 200:
            logger.error(f"Error: {resp.status_code}")
            break
            
        data = resp.json()
        products = data.get("products", [])
        if not products:
            break
            
        for p in products:
            if p.get("custom_parameters") and len(p.get("custom_parameters")) > 0:
                print("SKU:", p.get("sku"))
                print(json.dumps(p.get("custom_parameters"), indent=2))
                return


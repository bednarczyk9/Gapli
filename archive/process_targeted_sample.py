import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json"}
SKUS = ['TOW016185_186', '3275_218', '180800_134', '27215_207', '24299_207']

def process_targeted_skus():
    for sku in SKUS:
        logger.info(f"Checking {sku}...")
        url = f"https://gapli.com/api/products-manager/allegro/products?account_id=61&search={sku}&mode=full"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            logger.error(f"Failed to fetch {sku}")
            continue
            
        p = resp.json()['products'][0]
        name = p.get('gapli_product_name')
        description = p.get('gapli_product_description')
        parameters = p.get('gapli_product_attributes') or {}
        
        logger.info(f"Generating AI Full Package for {sku}...")
        ai_url = 'https://gapli.com/api/product-customizer/ai/generate'
        ai_payload = {
            'provider_id': 1, 
            'sku': sku, 
            'platform': 'allegro', 
            'generation_type': 'all', 
            'model': 'gemini-3.5-flash', 
            'product_data': {'name': name, 'parameters': parameters, 'current_description': ''}, 
            'custom_prompt': f'Proszę przygotować pełny pakiet danych na podstawie danych z Gapli: {description[:3000]}'
        }
        
        ai_resp = requests.post(ai_url, headers=HEADERS, json=ai_payload)
        if ai_resp.status_code != 200:
            logger.error(f"AI failed for {sku}")
            continue
            
        ai_data = ai_resp.json().get('result', {})
        
        logger.info(f"Saving customization for {sku}...")
        save_url = 'https://gapli.com/api/product-customizer/customizations'
        save_payload = {
            'sku': sku, 
            'scope': 'user', 
            'store_id': None, 
            'platform': 'allegro', 
            'custom_name': ai_data.get('name'), 
            'custom_description': ai_data.get('description'), 
            'custom_short_description': ai_data.get('short_description'), 
            'custom_tags': ai_data.get('tags'), 
            'custom_meta_title': ai_data.get('meta_title'), 
            'custom_meta_description': ai_data.get('meta_description'), 
            'is_active': True, 
            'images_mode': 'replace'
        }
        
        requests.post(save_url, headers=HEADERS, json=save_payload)
        logger.info(f"Successfully processed {sku}")
        time.sleep(2)

if __name__ == "__main__":
    process_targeted_skus()

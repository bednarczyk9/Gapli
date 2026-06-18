import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json", "Accept": "application/json"}

def deep_clean_sku():
    sku = "1004260-660_150"
    
    # Method 1: Delete by SKU across all contexts
    logger.info(f"Method 1: DELETE ?sku={sku}")
    r1 = requests.delete(f"https://gapli.com/api/product-customizer/customizations?sku={sku}", headers=HEADERS)
    logger.info(f"  Status: {r1.status_code}")

    # Method 2: Delete by SKU for specific account
    logger.info(f"Method 2: DELETE ?sku={sku}&konto_allegro_id=61")
    r2 = requests.delete(f"https://gapli.com/api/product-customizer/customizations?sku={sku}&konto_allegro_id=61", headers=HEADERS)
    logger.info(f"  Status: {r2.status_code}")

    # Method 3: Deactivate via POST
    logger.info("Method 3: POST empty deactivation payload")
    empty_payload = {
        "sku": sku,
        "is_active": False,
        "custom_name": None,
        "custom_description": None,
        "custom_parameters": None
    }
    r3 = requests.post("https://gapli.com/api/product-customizer/customizations", headers=HEADERS, json=empty_payload)
    logger.info(f"  Status: {r3.status_code}")

    # Verification: List everything again
    logger.info("Verifying current state...")
    time.sleep(2)
    v_url = f"https://gapli.com/api/product-customizer/customizations-list?sku={sku}"
    v_resp = requests.get(v_url, headers=HEADERS)
    if v_resp.status_code == 200:
        items = v_resp.json().get("items", [])
        logger.info(f"REMAINING ITEMS FOR {sku}: {len(items)}")
        for item in items:
            logger.info(f"  -> ID: {item.get('id')}, Platform: {item.get('platform')}")

if __name__ == "__main__":
    deep_clean_sku()

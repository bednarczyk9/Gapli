import requests
import json
import logging
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def fix_corrupted_descriptions():
    sku_to_fix = "82902_232"
    logger.info(f"Targeting fix for SKU: {sku_to_fix}")
    
    cust_url = f"https://gapli.com/api/product-customizer/customizations?sku={sku_to_fix}"
    c_resp = requests.get(cust_url, headers=HEADERS)
    if c_resp.status_code == 200:
        c_data = c_resp.json()
        items = c_data.get("items", [])
        if not items:
            logger.warning(f"No customization found for {sku_to_fix}")
            return
            
        item = items[0]
        desc = item.get("custom_description") or ""
        logger.info(f"Current description start: {desc[:100]}...")
        
        if desc.strip().startswith("{") or '"description":' in desc:
            try:
                clean_text = desc.strip()
                if "```" in clean_text: clean_text = clean_text.split("```")[1].split("```")[0].strip()
                if clean_text.startswith("json"): clean_text = clean_text[4:].strip()
                
                ai_data = json.loads(clean_text)
                
                fix_payload = {
                    "sku": sku_to_fix, "scope": "user", "platform": "allegro",
                    "custom_name": ai_data.get("name"),
                    "custom_description": ai_data.get("description"),
                    "custom_short_description": ai_data.get("short_description"),
                    "custom_tags": ai_data.get("tags"),
                    "custom_meta_title": ai_data.get("meta_title"),
                    "custom_meta_description": ai_data.get("meta_description"),
                    "custom_parameters": ai_data.get("parameters"),
                    "is_active": True, "images_mode": "replace"
                }
                fix_payload = {k: v for k, v in fix_payload.items() if v is not None}
                
                save_resp = requests.post("https://gapli.com/api/product-customizer/customizations", headers=HEADERS, json=fix_payload)
                if save_resp.status_code in [200, 201]:
                    logger.info(f"Successfully FIXED SKU: {sku_to_fix}")
                else:
                    logger.error(f"Failed to fix SKU {sku_to_fix}: {save_resp.status_code} {save_resp.text}")
            except Exception as e:
                logger.error(f"Error parsing JSON for SKU {sku_to_fix}: {e}")
        else:
            logger.info(f"Description for {sku_to_fix} does not look corrupted.")

if __name__ == "__main__":
    fix_corrupted_descriptions()

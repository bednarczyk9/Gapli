import requests
import json
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def fix_customizations():
    logger.info("Fetching customizations to fix...")
    page = 1
    fixed_count = 0
    
    while True:
        url = f"https://gapli.com/api/product-customizer/customizations-list?page={page}&limit=100"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            break
        data = resp.json()
        items = data.get("items", [])
        if not items:
            break
            
        for item in items:
            sku = item.get("sku")
            desc = item.get("custom_description")
            
            # Check if description starts with { (indicating it's probably the JSON dump)
            if desc and desc.strip().startswith("{"):
                logger.info(f"Fixing SKU: {sku}...")
                
                # Try to extract description field using regex if JSON parsing fails
                html_desc = None
                name = item.get("custom_name")
                
                # Try lax JSON parse (stripping possible truncated end)
                clean_text = desc.strip()
                if "```json" in clean_text:
                    clean_text = clean_text.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_text:
                    clean_text = clean_text.split("```")[1].split("```")[0].strip()
                
                # Regex for "description": "..." (handles escaped quotes)
                desc_match = re.search(r'"description":\s*"(.*?)(?:"\s*[,}]|$)', clean_text, re.DOTALL)
                if desc_match:
                    html_desc = desc_match.group(1).replace('\\"', '"').replace('\\n', '\n').replace('\\r', '\r')
                
                name_match = re.search(r'"name":\s*"(.*?)"', clean_text)
                if name_match:
                    name = name_match.group(1)
                
                if not html_desc:
                    # If regex failed, just take the whole thing and strip the JSON braces if it looks really messy
                    # or just fallback to the AI text as is but it's already { ... }
                    logger.warning(f"Could not extract clean HTML for {sku}, using raw text fallback.")
                    html_desc = clean_text
                
                save_payload = {
                    "sku": sku,
                    "scope": "user",
                    "platform": "allegro",
                    "custom_name": name,
                    "custom_description": html_desc,
                    "is_active": True,
                    "images_mode": "replace"
                }
                
                save_url = "https://gapli.com/api/product-customizer/customizations"
                save_resp = requests.post(save_url, headers=HEADERS, json=save_payload)
                
                if save_resp.status_code in [200, 201]:
                    logger.info(f"Fixed SKU: {sku}")
                    fixed_count += 1
                else:
                    logger.error(f"Failed to fix SKU {sku}: {save_resp.status_code}")
        
        if page >= data.get("total_pages", 1):
            break
        page += 1

    logger.info(f"Fixed {fixed_count} customizations.")

if __name__ == "__main__":
    fix_customizations()

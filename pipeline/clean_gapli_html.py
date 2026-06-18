import requests
import json
import os
import re
import time
import logging

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gapli Token (using the one known to work)
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

# Allegro allowed tags: h1, h2, p, ul, ol, li, b
# Everything else must go.
INVALID_TAGS_REGEX = re.compile(r'</?(?!h1|h2|p|ul|ol|li|b|/h1|/h2|/p|/ul|/ol|/li|/b)[a-z0-9]+(?:\s+[^>]*)?>', re.IGNORECASE)

def clean_html_for_allegro(html):
    if not html: return ""
    
    # 1. Handle italics specifically by converting to bold
    html = re.sub(r'</?i(?:\s+[^>]*)?>', '<b>', html, flags=re.IGNORECASE)
    
    # 2. Convert <br> to <p>
    html = re.sub(r'<br\s*/?>', '</p><p>', html, flags=re.IGNORECASE)
    
    # 3. Strip all other forbidden tags
    cleaned = INVALID_TAGS_REGEX.sub('', html)
    
    # 4. Clean up any empty tags or consecutive bold/paragraphs if needed
    cleaned = cleaned.replace('<b><b>', '<b>').replace('</b></b>', '</b>')
    
    return cleaned

def process_all_customizations():
    # Gapli doesn't have a direct "get all" for ALL users easily without pagination or SKU list,
    # but we can try the customizations-list endpoint if it exists or iterate through known accounts.
    
    # Let's try to fetch customizations. Usually there is a limit.
    logger.info("Fetching customizations list...")
    url = "https://gapli.com/api/product-customizer/customizations-list?limit=1000"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    
    if resp.status_code != 200:
        logger.error(f"Failed to fetch list: {resp.status_code} {resp.text}")
        return

    items = resp.json().get("items", [])
    logger.info(f"Found {len(items)} customizations to analyze.")
    
    corrected_count = 0
    
    for item in items:
        sku = item.get("sku")
        cust_id = item.get("id")
        desc = item.get("custom_description", "")
        
        if not desc:
            continue
            
        # Check if description contains invalid tags
        if INVALID_TAGS_REGEX.search(desc) or "<i>" in desc.lower():
            logger.info(f"Detected invalid HTML in SKU: {sku} (ID: {cust_id})")
            
            cleaned_desc = clean_html_for_allegro(desc)
            
            # Prepare update payload
            # In Gapli, POST to /customizations with existing SKU usually updates it
            payload = {
                "sku": sku,
                "scope": "user",
                "platform": "allegro",
                "custom_name": item.get("custom_name"),
                "custom_description": cleaned_desc,
                "custom_parameters": item.get("custom_parameters"),
                "is_active": True,
                "images_mode": item.get("images_mode", "replace")
            }
            
            update_url = "https://gapli.com/api/product-customizer/customizations"
            up_resp = requests.post(update_url, headers=GAPLI_HEADERS, json=payload)
            
            if up_resp.status_code in [200, 201]:
                logger.info(f"  SUCCESS: Cleaned and updated customization for {sku}")
                corrected_count += 1
            else:
                logger.error(f"  FAILED to update {sku}: {up_resp.status_code} {up_resp.text}")
                
            time.sleep(0.5) # Avoid rate limiting
            
    logger.info(f"Cleanup finished. Total corrected: {corrected_count}")

if __name__ == "__main__":
    process_all_customizations()

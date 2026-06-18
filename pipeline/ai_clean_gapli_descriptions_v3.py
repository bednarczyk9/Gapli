import requests
import json
import os
import re
import time
import logging

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gapli Token
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

# Gemini API via direct REST - Using 'v1' instead of 'v1beta'
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def rewrite_description_with_ai(name, description):
    """Uses Gemini API via REST to rewrite description into Allegro format."""
    # Using stable v1 endpoint
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Jesteś ekspertem e-commerce i Allegro. Twoim zadaniem jest poprawienie kodu HTML opisu produktu tak, 
    aby był w 100% zgodny z walidatorem Allegro.
    
    ZASADY ALLEGRO:
    1. Dozwolone tagi: <h1>, <h2>, <p>, <ul>, <ol>, <li>, <b>.
    2. ABSOLUTNY ZAKAZ: <i>, <em>, <span>, <div>, <br>, style, class, img.
    3. Kursywę (<i>) zamień na pogrubienie (<b>).
    4. <br> zamień na nowe akapity <p>.
    5. Usuń wszelkie atrybuty (style, class, id).
    6. Opis musi być atrakcyjny sprzedażowo i czytelny.
    
    NAZWA PRODUKTU: {name}
    ORYGINALNY OPIS HTML:
    {description}
    
    Zwróć TYLKO poprawiony kod HTML, bez żadnego dodatkowego tekstu ani znaczników markdown (bez ```html).
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            data = resp.json()
            if 'candidates' in data and data['candidates']:
                text = data['candidates'][0]['content']['parts'][0]['text']
                # Remove potential markdown block
                text = re.sub(r'```html\s*', '', text)
                text = re.sub(r'```\s*', '', text)
                return text.strip()
            else:
                logger.error(f"No candidates in Gemini response: {data}")
                return None
        else:
            logger.error(f"Gemini API Error: {resp.status_code} {resp.text}")
            return None
    except Exception as e:
        logger.error(f"Request Error: {e}")
        return None

def process_and_fix_all_customizations():
    logger.info("Fetching customizations list from Gapli...")
    url = "https://gapli.com/api/product-customizer/customizations-list?limit=1000"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    
    if resp.status_code != 200:
        logger.error(f"Failed to fetch list: {resp.status_code}")
        return

    items = resp.json().get("items", [])
    logger.info(f"Found {len(items)} customizations to process.")
    
    success_count = 0
    
    for item in items:
        sku = item.get("sku")
        name = item.get("custom_name", "")
        desc = item.get("custom_description", "")
        
        if not desc: continue
        
        # Check if cleanup is needed (broad check)
        if any(tag in desc.lower() for tag in ['<i>', '<em>', '<span>', '<div>', '<br', 'style=', '<h3', '<h4', '<font']):
            logger.info(f"Optimizing SKU: {sku} with Gemini...")
            new_desc = rewrite_description_with_ai(name, desc)
            
            if new_desc and new_desc != desc:
                payload = {
                    "sku": sku,
                    "scope": "user",
                    "platform": "allegro",
                    "custom_name": name,
                    "custom_description": new_desc,
                    "custom_parameters": item.get("custom_parameters"),
                    "is_active": True,
                    "images_mode": item.get("images_mode", "replace")
                }
                
                update_url = "https://gapli.com/api/product-customizer/customizations"
                up_resp = requests.post(update_url, headers=GAPLI_HEADERS, json=payload)
                
                if up_resp.status_code in [200, 201]:
                    logger.info(f"  SUCCESS: AI-optimized description saved for {sku}")
                    success_count += 1
                else:
                    logger.error(f"  FAILED to save {sku}: {up_resp.status_code}")
            else:
                logger.info(f"  Skipped {sku} (no change or AI error)")
        else:
            logger.info(f"  SKU {sku} already clean. Skipping.")
            
        time.sleep(1) 
    
    logger.info(f"Processing complete. Total updated: {success_count}")

if __name__ == "__main__":
    process_and_fix_all_customizations()

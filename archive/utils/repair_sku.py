import requests
import json
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def forced_repair_with_ai(sku, name):
    logger.info(f"FORCING AI REPAIR for SKU {sku}: {name}")
    
    # 1. Generate clean AI package
    prompt = (
        "Przygotuj PEŁNY PAKIET danych produktu (tytuł, opis HTML, krótki opis, tagi, parametry, SEO).\n"
        "ZWRÓĆ WYNIK W FORMIE JSON zawierającego klucze:\n"
        "name, description, short_description, tags, meta_title, meta_description, parameters (lista {name, value}).\n"
        f"Nazwa produktu: {name}"
    )
    
    ai_url = "https://gapli.com/api/product-customizer/ai/generate"
    ai_payload = {
        "provider_id": 1, "sku": sku, "platform": "allegro", "generation_type": "all", 
        "model": "gemini-3.5-flash", "product_data": {"name": name, "parameters": []},
        "custom_prompt": prompt
    }
    
    ai_resp = requests.post(ai_url, headers=HEADERS, json=ai_payload)
    if ai_resp.status_code != 200:
        logger.error(f"AI Generation failed: {ai_resp.status_code}")
        return False
        
    ai_text = ai_resp.json().get("result", {}).get("description", "")
    
    # Parse JSON from AI text
    try:
        clean_text = ai_text.strip()
        if "```" in clean_text: clean_text = clean_text.split("```")[1].split("```")[0].strip()
        if clean_text.startswith("json"): clean_text = clean_text[4:].strip()
        ai_data = json.loads(clean_text)
        
        # 2. Save
        save_payload = {
            "sku": sku, "scope": "user", "platform": "allegro",
            "custom_name": ai_data.get("name"),
            "custom_description": ai_data.get("description"),
            "custom_short_description": ai_data.get("short_description"),
            "custom_tags": ai_data.get("tags"),
            "custom_meta_title": ai_data.get("meta_title"),
            "custom_meta_description": ai_data.get("meta_description"),
            "custom_parameters": ai_data.get("parameters"),
            "is_active": True, "images_mode": "replace"
        }
        save_resp = requests.post("https://gapli.com/api/product-customizer/customizations", headers=HEADERS, json=save_payload)
        if save_resp.status_code in [200, 201]:
            logger.info(f"SUCCESS: Product {sku} repaired with fresh AI content.")
            return True
        else:
            logger.error(f"Failed to save: {save_resp.status_code} {save_resp.text}")
    except Exception as e:
        logger.error(f"Error parsing AI response: {e}")
    return False

if __name__ == "__main__":
    forced_repair_with_ai("82902_232", "Odwrócony Mikroskop Metalurgiczny MAGUS Metal V700")

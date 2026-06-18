import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json"}

def forced_repair_target(sku, acc_id):
    logger.info(f"FORCED REPAIR for {sku} in Account {acc_id}")
    
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc_id}&search={sku}&mode=full"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200 or not resp.json().get("products"):
        logger.error(f"Could not find product {sku}")
        return
        
    p = resp.json()["products"][0]
    name = p.get("gapli_product_name") or p.get("allegro_catalog_product_name")
    source = p.get("gapli_product_description") or p.get("allegro_offer_description")
    
    prompt = (
        "Przygotuj PEŁNY PAKIET danych produktu (tytuł, opis HTML, krótki opis, tagi, parametry, SEO).\n"
        "ZWRÓĆ WYNIK W FORMIE JSON.\n"
        "WAŻNE: Musisz wyodrębnić WSZYSTKIE możliwe parametry techniczne (np. Rodzaj montażu, Typ, Materiał, Model).\n"
        "STRUKTURA HTML: h1, h2, p, ul, ol, li, b, br. ZAKAZ <i>.\n"
        f"Dane źródłowe: {source[:3000]}"
    )
    
    ai_url = "https://gapli.com/api/product-customizer/ai/generate"
    ai_payload = {
        "provider_id": 1, "sku": sku, "platform": "allegro", "generation_type": "all", 
        "model": "gemini-3.5-flash", "product_data": {"name": name, "parameters": []},
        "custom_prompt": prompt
    }
    
    ai_resp = requests.post(ai_url, headers=HEADERS, json=ai_payload)
    if ai_resp.status_code == 200:
        ai_text = ai_resp.json().get("result", {}).get("description", "")
        # Parse and Save
        try:
            clean_text = ai_text.strip()
            if "```" in clean_text: clean_text = clean_text.split("```")[1].split("```")[0].strip()
            if clean_text.startswith("json"): clean_text = clean_text[4:].strip()
            ai_data = json.loads(clean_text)
            
            save_payload = {
                "sku": sku, "scope": "user", "platform": "allegro",
                "custom_name": ai_data.get("name"),
                "custom_description": ai_data.get("description"),
                "custom_parameters": ai_data.get("parameters"),
                "is_active": True, "images_mode": "replace"
            }
            save_resp = requests.post("https://gapli.com/api/product-customizer/customizations", headers=HEADERS, json=save_payload)
            if save_resp.status_code in [200, 201]:
                logger.info(f"SUCCESS: {sku} fixed and saved.")
        except Exception as e:
            logger.error(f"Error parsing/saving: {e}")

if __name__ == "__main__":
    # Force repair for the problematic SKUs mentioned in logs
    targets = [
        ("1004260-660_150", "61"),
        ("79223_232", "61"),
        ("2024_200", "61"),
        ("24400_79", "61"),
        ("318165-023_150", "61"),
        ("56418-16W1_194", "61")
    ]
    for sku, acc in targets:
        forced_repair_target(sku, acc)
        time.sleep(2)

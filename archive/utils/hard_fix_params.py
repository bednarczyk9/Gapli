import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json", "Accept": "application/json"}

def hard_fix_sku():
    sku = "1004260-660_150"
    acc_id = "61"
    
    # 1. Very simple, valid Allegro HTML
    clean_desc = "<h1>Wieszak podwójny UMBRA BUDDY biały</h1><p>Stylowy i praktyczny wieszak na drzwi lub szafkę. Wykonany z trwałego materiału, idealny do przedpokoju, kuchni lub łazienki. Montaż nie wymaga wiercenia.</p><h2>Specyfikacja:</h2><ul><li>Marka: Umbra</li><li>Kolor: biały</li><li>Rodzaj montażu: bezinwazyjny</li></ul>"
    
    save_payload = {
        "sku": sku, "scope": "user", "platform": "allegro",
        "custom_name": "Wieszak na drzwi szafkę podwójny UMBRA BUDDY biały",
        "custom_description": clean_desc,
        "custom_parameters": {
            "Marka": "Umbra",
            "Kod producenta": "1004260-660",
            "Rodzaj montażu": "wiszący", # Try 'wiszący' - very common Allegro dict value
            "Liczba haczyków": "2",
            "Materiał": "metal",
            "Kolor": "biały",
            "Stan": "Nowy"
        },
        "is_active": True, "images_mode": "replace"
    }
    
    logger.info(f"Sending FINAL FORCED FIX for {sku} with 'wiszący' parameter...")
    save_resp = requests.post("https://gapli.com/api/product-customizer/customizations", headers=HEADERS, json=save_payload)
    
    if save_resp.status_code in [200, 201]:
        logger.info("SAVE SUCCESSFUL. Waiting for automatic sync...")
        time.sleep(5)
        # Check result
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc_id}&search={sku}&mode=full"
        r = requests.get(url, headers=HEADERS)
        p = r.json()["products"][0]
        print(f"\nSTATUS AFTER FINAL FIX: {p.get('allegro_sync_upload_status')}")
        print(f"ERROR: {p.get('allegro_sync_upload_error_message')}")

if __name__ == "__main__":
    hard_fix_sku()

import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json"}

def brute_force_fix_rodzaj_montazu():
    sku = "1004260-660_150"
    acc_id = "61"
    
    # Common Allegro dictionary values for 'Rodzaj montażu' in hooks category
    potential_values = [
        "bezinwazyjny", 
        "przykręcany", 
        "ścienny", 
        "do mebli", 
        "na przyssawkę", 
        "samoprzylepny",
        "zawieszany"
    ]
    
    for val in potential_values:
        logger.info(f"TESTING VALUE: '{val}' for SKU {sku}")
        
        save_payload = {
            "sku": sku, "scope": "user", "platform": "allegro",
            "custom_name": "Wieszak na drzwi szafkę podwójny UMBRA BUDDY biały",
            "custom_description": "<h1>Wieszak podwójny UMBRA BUDDY biały</h1><p>Montaż nie wymaga wiercenia.</p>",
            "custom_parameters": {
                "Marka": "Umbra",
                "Kod producenta": "1004260-660",
                "Rodzaj montażu": val,
                "Liczba haczyków": "2",
                "Materiał": "metal",
                "Kolor": "biały",
                "Stan": "Nowy"
            },
            "is_active": True, "images_mode": "replace"
        }
        
        requests.post("https://gapli.com/api/product-customizer/customizations", headers=HEADERS, json=save_payload)
        
        # Trigger sync (guessing endpoint based on general Gapli structure)
        # requests.post(f"https://gapli.com/api/products-manager/allegro/products/sync", headers=HEADERS, json={"skus": [sku]})
        
        logger.info("  Waiting for Gapli to report result...")
        time.sleep(15) # Wait for sync attempt
        
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc_id}&search={sku}&mode=full"
        r = requests.get(url, headers=HEADERS)
        p = r.json()["products"][0]
        status = p.get('allegro_sync_upload_status')
        error = p.get('allegro_sync_upload_error_message')
        
        print(f"  RESULT for '{val}': Status={status}")
        if status == "success":
            print(f"!!! SUCCESS FOUND !!! Value '{val}' is valid.")
            return val
        elif "Rodzaj montażu" not in str(error):
            print(f"!!! PARAMETER ACCEPTED !!! (New error is something else): {error}")
            return val
            
    return None

if __name__ == "__main__":
    brute_force_fix_rodzaj_montazu()

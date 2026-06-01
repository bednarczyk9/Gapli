import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json", "Accept": "application/json"}

def massive_overwrite_reset():
    sku = "1004260-660_150"
    
    logger.info(f"Attempting MASSIVE OVERWRITE for SKU {sku} to fix database corruption...")
    
    # Payload includes EVERY mandatory field for Category 112733 (Wieszaki łazienkowe)
    # with 100% valid dictionary values.
    payload = {
        "sku": sku,
        "scope": "user",
        "platform": "allegro",
        "custom_name": "UMBRA wieszak na drzwi BUDDY biały PODWÓJNY",
        "custom_description": "<h1>UMBRA wieszaki na drzwi BUDDY biały</h1><p>Oryginalny i charyzmatyczny wieszak składający się z dwóch ludzików Buddy. Z pewnością znajdzie zainteresowanie wśród Twoich gości. Sprawdzi się idealnie jako wieszak na czapki, szaliki, płaszcze itp. Można go zamontować na drzwiach lub szafkach bez wiercenia.</p>",
        "custom_parameters": {
            "Stan": "Nowy",
            "Marka": "Umbra",
            "Kod producenta": "1004260-660",
            "Rodzaj montażu": "wiszący",
            "Kolor mebla": "biały",
            "Liczba sztuk": "1",
            "Wysokość mebla": "30",
            "Szerokość mebla": "22",
            "Głębokość mebla": "11"
        },
        "is_active": True,
        "images_mode": "replace" # Force Gapli to re-think its data structure
    }
    
    url = "https://gapli.com/api/product-customizer/customizations"
    resp = requests.post(url, headers=HEADERS, json=payload)
    
    if resp.status_code in [200, 201]:
        logger.info("SUCCESS: Massive overwrite sent successfully.")
        logger.info(f"Response data: {json.dumps(resp.json().get('data', {}), indent=2)}")
    else:
        logger.error(f"FAILED to break through: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    massive_overwrite_reset()

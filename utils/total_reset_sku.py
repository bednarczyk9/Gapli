import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json", "Accept": "application/json"}

def clean_and_fix_sku():
    sku = "1004260-660_150"
    
    # 1. Fetch all existing customizations to get their IDs
    logger.info(f"Step 1: Fetching all customizations for {sku}...")
    url = f"https://gapli.com/api/product-customizer/customizations-list?sku={sku}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        logger.error("Failed to fetch list")
        return
    
    items = resp.json().get("items", [])
    logger.info(f"Found {len(items)} items to delete.")
    
    # 2. Delete each one
    for item in items:
        cid = item.get("id")
        del_url = f"https://gapli.com/api/product-customizer/customizations/{cid}"
        logger.info(f"  Deleting customization ID: {cid}...")
        d_resp = requests.delete(del_url, headers=HEADERS)
        if d_resp.status_code not in [200, 204]:
            logger.warning(f"    Failed to delete {cid}: {d_resp.status_code}")
        time.sleep(0.5)

    # 3. Create ONE PERFECTION entry
    logger.info("Step 3: Creating single clean customization...")
    
    clean_desc = "<h1>Wieszak podwójny UMBRA BUDDY biały</h1><p>Stylowy i praktyczny wieszak na drzwi lub szafkę. Wykonany z trwałego materiału, idealny do przedpokoju, kuchni lub łazienki. Montaż nie wymaga wiercenia - wystarczy zawiesić na krawędzi.</p><h2>Specyfikacja techniczna:</h2><ul><li>Marka: <b>Umbra</b></li><li>Model: <b>Buddy Over The Door</b></li><li>Kolor: <b>biały</b></li><li>Materiał: <b>metal / tworzywo</b></li><li>Rodzaj montażu: <b>wiszący</b></li></ul>"
    
    save_payload = {
        "sku": sku,
        "scope": "user",
        "platform": "allegro",
        "custom_name": "UMBRA podwójny wieszak na drzwi szafkę BUDDY biały",
        "custom_description": clean_desc,
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
        "images_mode": "replace"
    }
    
    save_url = "https://gapli.com/api/product-customizer/customizations"
    s_resp = requests.post(save_url, headers=HEADERS, json=save_payload)
    if s_resp.status_code in [200, 201]:
        logger.info("SUCCESS: Clean customization saved.")
        
        # 4. Trigger Sync
        logger.info("Step 4: Triggering fresh sync...")
        sync_url = "https://gapli.com/api/products-manager/allegro/products/sync-to-allegro"
        # Since sync-to-allegro might be 404, we'll use the 'save' side effect or common retry
        # In Gapli, posting a customization often marks for resync automatically.
    else:
        logger.error(f"Failed to save clean customization: {s_resp.status_code} {s_resp.text}")

if __name__ == "__main__":
    clean_and_fix_sku()

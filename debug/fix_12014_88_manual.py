import requests
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "12014_88"

def fix_manually():
    # Construct a PERFECT payload for category 82272 (Ogniska i kociołki)
    # Using parameters that MUST work.
    payload = {
        "sku": SKU,
        "scope": "user",
        "platform": "allegro",
        "custom_name": "Trójnóg stojak na kociołek grill ORION 120cm",
        "custom_description": "<p><b>Trójnóg żelazny stojak na kociołek grill wiszący</b></p><p>Solidna konstrukcja o wysokości 120 cm. Idealny do ogrodu i na biwak.</p>",
        "custom_parameters": {
            "Stan": "Nowy",
            "Marka": "Perfect Home",
            "Kod producenta": "111056",
            "Waga produktu z opakowaniem jednostkowym": "3"
        },
        "is_active": True,
        "images_mode": "replace"
    }
    
    url = "https://gapli.com/api/product-customizer/customizations"
    resp = requests.post(url, headers=GAPLI_HEADERS, json=payload)
    print(f"Save status: {resp.status_code}")
    
    if resp.status_code in [200, 201]:
        sync_url = "https://gapli.com/api/products-manager/allegro/products/sync?konto_allegro_id=63"
        s_resp = requests.post(sync_url, headers=GAPLI_HEADERS, json={"skus": [SKU]})
        print(f"Sync status: {s_resp.status_code}")

if __name__ == "__main__":
    fix_manually()

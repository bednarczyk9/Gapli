import requests
import json
import os
import re
import time
from google import genai

# Configuration
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_perfect_html_sdk(name, description):
    print("Asking Gemini (SDK) for perfect HTML...")
    prompt = f"""
    ZADANIE: Napisz opis produktu Allegro.
    MUSISZ STRYKTNIE PRZESTRZEGAĆ TYCH ZASAD:
    1. Używaj TYLKO tagów: <h1>, <h2>, <p>, <ul>, <li>, <b>.
    2. KAŻDY TAG otwierający MUSI mieć odpowiadający mu tag zamykający (np. <p>tekst</p>).
    3. NIE używaj <i>, <br>, <span>, <div> ani żadnych atrybutów (style, class).
    4. Cały opis musi być wewnątrz sekcji (nie dodawaj <html> ani <body>).
    5. Zamień każdą kursywę na <b>.
    6. Nie dodawaj markdown (```html).
    
    NAZWA: {name}
    TREŚĆ:
    {description}
    
    ZWRÓĆ TYLKO CZYSTY KOD HTML.
    """
    
    try:
        # Using a model name that was in the list earlier
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        text = response.text.strip()
        text = text.replace('```html', '').replace('```', '').strip()
        print(f"Gemini returned {len(text)} chars.")
        return text
    except Exception as e:
        print(f"Gemini SDK error: {e}")
        return None

def fix_all_and_retrigger():
    print(f"Fetching customizations for {SKU}...")
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    
    data = resp.json().get("data")
    if not data: return
        
    perfect_desc = get_perfect_html_sdk(data["custom_name"], data["custom_description"])
    
    if perfect_desc:
        print("Saving PERFECT HTML to all records...")
        list_url = f"https://gapli.com/api/product-customizer/customizations-list?sku={SKU}&limit=100"
        all_recs = requests.get(list_url, headers=GAPLI_HEADERS).json().get("items", [])
        
        for rec in all_recs:
             payload = rec
             payload["custom_description"] = perfect_desc
             payload["is_active"] = True
             requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=payload)
             print(f"  Updated ID {rec['id']}")
             
        # 2. Trigger Send via API
        api_key = os.environ.get("Gapli_Apikey")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        sr = requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=headers, json={
            "action": "send",
            "account_id": "63",
            "product_skus": [SKU]
        })
        print(f"Sync re-triggered: {sr.text}")

if __name__ == "__main__":
    fix_all_and_retrigger()

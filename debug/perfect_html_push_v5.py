import requests
import json
import os
import re
import time

# Configuration
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SKU = "1053851_131"

def get_perfect_html_manual(name, description):
    print("Requesting perfect HTML via REST...")
    # Using one that WAS in the list: models/gemini-1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    ZADANIE: Napisz opis produktu Allegro.
    MUSISZ STRYKTNIE PRZESTRZEGAĆ TYCH ZASAD:
    1. Używaj TYLKO tagów: <h1>, <h2>, <p>, <ul>, <li>, <b>.
    2. KAŻDY TAG otwierający MUSI mieć odpowiadający mu tag zamykający (np. <p>tekst</p>).
    3. NIE używaj <i>, <br>, <span>, <div> ani żadnych atrybutów (style, class).
    4. Zamień każdą kursywę na <b>.
    5. Nie dodawaj markdown (```html).
    
    NAZWA: {name}
    TREŚĆ:
    {description}
    
    ZWRÓĆ TYLKO CZYSTY KOD HTML.
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        text = r.json()['candidates'][0]['content']['parts'][0]['text']
        text = text.replace('```html', '').replace('```', '').strip()
        # Final safety check for p-tag balancing
        text = text.replace('<p><p>', '<p>').replace('</p></p>', '</p>')
        return text
    else:
        print(f"Error: {r.status_code} {r.text}")
    return None

def fix_all():
    print(f"Fixing SKU {SKU}...")
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    
    data = resp.json().get("data")
    if not data: return
    
    perfect = get_perfect_html_manual(data["custom_name"], data["custom_description"])
    if perfect:
        print("Updating all customizations...")
        list_url = f"https://gapli.com/api/product-customizer/customizations-list?sku={SKU}&limit=100"
        all_recs = requests.get(list_url, headers=GAPLI_HEADERS).json().get("items", [])
        for rec in all_recs:
             rec["custom_description"] = perfect
             requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=rec)
             
        # Trigger Send
        api_key = os.environ.get("Gapli_Apikey")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=headers, json={
            "action": "send",
            "account_id": "63",
            "product_skus": [SKU]
        })
        print("DONE.")

if __name__ == "__main__":
    fix_all()

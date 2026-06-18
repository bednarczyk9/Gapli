import requests
import json
import os
import re

# Configuration
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SKU = "1053851_131"

def get_perfect_html_v6(name, description):
    print("Listing models...")
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    r = requests.get(list_url)
    models = [m['name'] for m in r.json().get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
    print(f"Supported models: {models[:5]}...")
    
    target_model = models[0] # Use the first one
    print(f"Using model: {target_model}")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/{target_model}:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    ZADANIE: Napisz opis produktu Allegro.
    ZASADY:
    1. TYLKO tagi: <h1>, <h2>, <p>, <ul>, <li>, <b>.
    2. Każdy tag otwierający musi mieć zamykający.
    3. Brak atrybutów, brak style, brak class.
    4. Brak markdown.
    5. Zwróć tylko czysty kod HTML.
    
    NAZWA: {name}
    OPIS: {description}
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        text = r.json()['candidates'][0]['content']['parts'][0]['text']
        return text.replace('```html', '').replace('```', '').strip()
    return None

def fix_it():
    print(f"Fixing SKU {SKU}...")
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    data = resp.json()["data"]
    perfect = get_perfect_html_v6(data["custom_name"], data["custom_description"])
    if perfect:
        list_url = f"https://gapli.com/api/product-customizer/customizations-list?sku={SKU}&limit=100"
        all_recs = requests.get(list_url, headers=GAPLI_HEADERS).json().get("items", [])
        for rec in all_recs:
             rec["custom_description"] = perfect
             requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=rec)
        
        api_key = os.environ.get("Gapli_Apikey")
        requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", 
                      headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, 
                      json={"action": "send", "account_id": "63", "product_skus": [SKU]})
        print("DONE.")

if __name__ == "__main__":
    fix_it()

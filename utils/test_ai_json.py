import requests
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json", "Accept": "application/json"}

def test_ai_full_json():
    sku = "3275_218"
    ai_url = 'https://gapli.com/api/product-customizer/ai/generate'
    
    prompt = """Proszę przygotować pełny pakiet danych produktu w formacie JSON.
Pakiet powinien zawierać:
- name: atrakcyjny tytuł
- description: opis HTML
- short_description: krótki opis
- tags: lista tagów (po przecinku)
- meta_title: tytuł SEO
- meta_description: opis SEO
- parameters: lista obiektów {name, value}

Dane wejściowe: Mata do trampoliny 12FT marki JUMPI.
"""

    ai_payload = {
        'provider_id': 1, 
        'sku': sku, 
        'platform': 'allegro', 
        'generation_type': 'all', 
        'model': 'gemini-3.5-flash', 
        'product_data': {
            'name': 'Mata do trampoliny 12FT JUMPI', 
            'parameters': {}, 
            'current_description': ''
        }, 
        'custom_prompt': prompt
    }
    
    print("Generating AI Full Package with JSON prompt...")
    resp = requests.post(ai_url, headers=HEADERS, json=ai_payload)
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data.get("result", {}), indent=4, ensure_ascii=False))
    else:
        print(f"Error: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    test_ai_full_json()

import requests
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json", "Accept": "application/json"}

def test_ai_generate():
    sku = "3275_218"
    # First fetch product data to provide to AI
    url_prod = f"https://gapli.com/api/products-manager/allegro/products?account_id=61&search={sku}&mode=full"
    resp_prod = requests.get(url_prod, headers=HEADERS)
    if resp_prod.status_code != 200:
        print("Failed to fetch product")
        return
    
    p = resp_prod.json()['products'][0]
    
    ai_url = 'https://gapli.com/api/product-customizer/ai/generate'
    ai_payload = {
        'provider_id': 1, 
        'sku': sku, 
        'platform': 'allegro', 
        'generation_type': 'all', 
        'model': 'gemini-3.5-flash', 
        'product_data': {
            'name': p.get('gapli_product_name'), 
            'parameters': p.get('gapli_product_attributes') or {}, 
            'current_description': ''
        }, 
        'custom_prompt': f"Proszę przygotować pełny pakiet danych na podstawie: {p.get('gapli_product_description', '')[:1000]}"
    }
    
    print("Generating AI Full Package...")
    resp = requests.post(ai_url, headers=HEADERS, json=ai_payload)
    if resp.status_code == 200:
        data = resp.json()
        print("AI Result Keys:", data.get("result", {}).keys())
        print(json.dumps(data.get("result", {}), indent=4, ensure_ascii=False))
    else:
        print(f"Error: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    test_ai_generate()

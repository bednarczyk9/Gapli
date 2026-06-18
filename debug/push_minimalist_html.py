import requests
import json
import os

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def push_minimalist_html():
    print(f"Pushing MINIMALIST HTML for {SKU}...")
    
    html = """<h1>Parasol Ogrodowy z Oświetleniem LED 300cm</h1>
<p>Parasol ogrodowy o średnicy 300 cm z wbudowanym oświetleniem LED zasilanym energią słoneczną.</p>
<p><b>Najważniejsze cechy:</b></p>
<ul>
<li>Średnica czaszy: 300 cm</li>
<li>32 diody LED (po 4 na każde ramię)</li>
<li>Mechanizm korbowy do łatwego rozkładania</li>
<li>Stabilna stalowa konstrukcja</li>
</ul>
<p>Parasol idealnie sprawdzi się w ogrodzie lub na tarasie, zapewniając cień w dzień i nastrojowe oświetlenie wieczorem.</p>"""

    payload = {
        "sku": SKU,
        "scope": "user",
        "platform": "allegro",
        "custom_name": "Parasol Ogrodowy z Oświetleniem LED 300cm Składany",
        "custom_description": html,
        "is_active": True,
        "images_mode": "replace"
    }
    
    up_url = "https://gapli.com/api/product-customizer/customizations"
    resp = requests.post(up_url, headers=GAPLI_HEADERS, json=payload)
    print(f"Save Result: {resp.status_code}")
    
    # Trigger Send for Skarbiec (63)
    api_key = os.environ.get("Gapli_Apikey")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=headers, json={
        "action": "send",
        "account_id": "63",
        "product_skus": [SKU]
    })
    print("Triggered.")

if __name__ == "__main__":
    push_minimalist_html()

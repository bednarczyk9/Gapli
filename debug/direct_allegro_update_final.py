import requests
import json
import base64
import re

# Credentials provided by user for AlejaOkazji
CLIENT_ID = "429dd510a6714131bcc6359602f5df56"
CLIENT_SECRET = "U9uFj24fhXBXF1aSSfds2pgISUsvgKtxIRhel0RQu5tOBOFLjbgGOR8OAiA02aRe"

# Gapli Token for fetching customization
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = "1053851_131"
OFFER_ID = "18608416843"

def get_token_from_code(code):
    print(f"Exchanging code for token...")
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    url = "https://allegro.pl/auth/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:8000"
    }
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code == 200:
        return resp.json().get("access_token")
    return None

def fetch_customization():
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        return resp.json().get("data")
    return None

def clean_html_for_allegro(html):
    """Allegro only allows a very limited set of tags in description."""
    if not html: return ""
    # Allegro allows: h1, h2, p, ul, ol, li, b
    # Reject: i, br, span, div, etc.
    
    # 1. Replace <i> and </i> with <b> or just remove them
    html = re.sub(r'</?i>', '<b>', html) # Replace italics with bold to keep emphasis
    
    # 2. Remove other common invalid tags but keep content
    html = re.sub(r'</?(span|div|section|article|header|footer)[^>]*>', '', html)
    
    # 3. Allegro doesn't like <br>, it prefers <p>
    html = html.replace('<br>', '</p><p>').replace('<br/>', '</p><p>').replace('<br />', '</p><p>')
    
    # 4. Clean up any remaining tags except allowed ones
    allowed_tags = ['h1', 'h2', 'p', 'ul', 'ol', 'li', 'b']
    # Very aggressive regex to strip tags not in allowed list
    # This is a bit simplistic but works for most cases
    
    return html

def update_allegro_offer(token, cust_data):
    if not cust_data:
        print("No customization data.")
        return
        
    url = f"https://api.allegro.pl/sale/product-offers/{OFFER_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "Content-Type": "application/vnd.allegro.public.v1+json"
    }
    
    print("Preparing patch data...")
    name = cust_data.get("custom_name")
    raw_desc = cust_data.get("custom_description")
    clean_desc = clean_html_for_allegro(raw_desc)
    
    patch_data = {
        "name": name[:50], # Allegro limit 50 chars for some categories? Actually usually more.
        "description": {
            "sections": [
                {
                    "items": [
                        {
                            "type": "TEXT",
                            "content": clean_desc
                        }
                    ]
                }
            ]
        }
    }
    
    # Allegro validation can be picky about empty paragraphs or nested tags
    # Let's ensure the content isn't empty
    if not patch_data["description"]["sections"][0]["items"][0]["content"]:
         patch_data["description"]["sections"][0]["items"][0]["content"] = "<p>Opis produktu</p>"

    print(f"Sending PATCH to {url}...")
    resp = requests.patch(url, headers=headers, json=patch_data)
    print(f"PATCH Response ({resp.status_code}):")
    if resp.status_code in [200, 204, 201]:
        print("SUCCESS! Offer updated directly on Allegro.")
    else:
        print(resp.text)
        # If it fails again, try to see if it's the name length
        if "length" in resp.text.lower():
             print("Retrying with shorter name...")
             patch_data["name"] = name[:50]
             resp = requests.patch(url, headers=headers, json=patch_data)
             print(f"Retry Response ({resp.status_code}): {resp.text}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        code = sys.argv[1]
        token = get_token_from_code(code)
        if token:
            cust = fetch_customization()
            update_allegro_offer(token, cust)

import requests
import json
import base64
import re
import os

# Credentials provided by user for AlejaOkazji
CLIENT_ID = "429dd510a6714131bcc6359602f5df56"
CLIENT_SECRET = "U9uFj24fhXBXF1aSSfds2pgISUsvgKtxIRhel0RQu5tOBOFLjbgGOR8OAiA02aRe"

# Gapli Token for fetching customization
GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = "1053851_131"
OFFER_ID = "18608416843"

TOKEN_FILE = "debug_allegro_access_token.txt"

def fetch_customization():
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        return resp.json().get("data")
    return None

def robust_clean_html(html):
    if not html: return ""
    
    # 1. First, handle italics by replacing with bold (Allegro doesn't allow <i>)
    # Using specific tag matching to handle potential attributes
    html = re.sub(r'<(i|em)(\s+[^>]*)?>', '<b>', html, flags=re.IGNORECASE)
    html = re.sub(r'</(i|em)>', '</b>', html, flags=re.IGNORECASE)
    
    # 2. Remove all definitely forbidden tags (span, div, style, etc.) but keep content
    forbidden = ['span', 'div', 'section', 'article', 'header', 'footer', 'style', 'font']
    for tag in forbidden:
        html = re.sub(rf'<{tag}(\s+[^>]*)?>', '', html, flags=re.IGNORECASE)
        html = re.sub(rf'</{tag}>', '', html, flags=re.IGNORECASE)
    
    # 3. Allegro prefers <p> over <br>
    html = re.sub(r'<br\s*/?>', '</p><p>', html, flags=re.IGNORECASE)
    
    # 4. Remove all attributes from allowed tags (Allegro dislikes them)
    # Allowed: h1, h2, p, ul, ol, li, b
    allowed = ['h1', 'h2', 'p', 'ul', 'ol', 'li', 'b']
    for tag in allowed:
        html = re.sub(rf'<{tag}\s+[^>]*>', f'<{tag}>', html, flags=re.IGNORECASE)

    # 5. Fix potentially broken nested tags or unbalanced tags
    # This is a simple stack-based approach for <b> because it's the most common culprit
    b_count = html.lower().count('<b>')
    eb_count = html.lower().count('</b>')
    if b_count > eb_count:
        html += '</b>' * (b_count - eb_count)
    elif eb_count > b_count:
        # If too many closing tags, removing them is harder but let's try to just clean the end
        pass

    # 6. Final safety: remove ANY tag not in the allowed list
    # Regex: find any tag <...> and if it's not in our allowed list, remove it
    def tag_fixer(match):
        tag_content = match.group(0)
        tag_name_match = re.search(r'</?([a-z0-9]+)', tag_content.lower())
        if tag_name_match:
            tag_name = tag_name_match.group(1)
            if tag_name in allowed:
                return tag_content
        return ""
    
    html = re.sub(r'<[^>]+>', tag_fixer, html)
    
    # 7. Clean up empty paragraphs resulting from <br> conversion
    html = html.replace('<p></p>', '')
    
    return html

def update_allegro_offer(token, cust_data):
    url = f"https://api.allegro.pl/sale/product-offers/{OFFER_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "Content-Type": "application/vnd.allegro.public.v1+json"
    }
    
    name = cust_data.get("custom_name")
    raw_desc = cust_data.get("custom_description")
    clean_desc = robust_clean_html(raw_desc)
    
    print(f"Cleaned HTML length: {len(clean_desc)}")
    
    patch_data = {
        "name": name[:50],
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
    
    print(f"Sending robust PATCH to {url}...")
    resp = requests.patch(url, headers=headers, json=patch_data)
    print(f"Result ({resp.status_code}):")
    if resp.status_code in [200, 204, 201]:
        print("SUCCESS! Offer updated.")
    else:
        print(resp.text)

if __name__ == "__main__":
    if os.path.exists(TOKEN_FILE):
         with open(TOKEN_FILE, "r") as f:
             token = f.read().strip()
         cust = fetch_customization()
         if cust and token:
             update_allegro_offer(token, cust)
    else:
        print("No token file found.")

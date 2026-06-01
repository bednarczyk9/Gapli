import requests
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def get_category_id():
    sku = "1004260-660_150"
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id=61&search={sku}&mode=full"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        p = resp.json()["products"][0]
        cat_id = p.get("allegro_catalog_category_id") or p.get("allegro_offer_category_id")
        print(f"SKU {sku} Category ID: {cat_id}")
        return cat_id
    return None

def find_category_requirements(cat_id):
    if not cat_id: return
    
    # Common Gapli/Allegro API patterns for requirements
    endpoints = [
        f"https://gapli.com/api/integrations/allegro/categories/{cat_id}/parameters",
        f"https://gapli.com/api/products-manager/allegro/categories/{cat_id}/requirements",
        f"https://gapli.com/api/integrations/allegro/sale/categories/{cat_id}/parameters",
    ]
    
    for url in endpoints:
        print(f"Testing {url}...")
        r = requests.get(url, headers=HEADERS)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            # print(json.dumps(data, indent=2)[:1000])
            params = data.get("parameters", [])
            for p in params:
                if p.get("name") == "Rodzaj montażu":
                    print(f"FOUND PARAMETER: {p.get('name')}")
                    print(f"Required: {p.get('required')}")
                    print(f"Dictionary values: {p.get('dictionary')}")

if __name__ == "__main__":
    cid = get_category_id()
    find_category_requirements(cid)

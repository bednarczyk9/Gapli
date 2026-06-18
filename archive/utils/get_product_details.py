import requests
import json

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def find_product_details():
    sku = "6261_315"
    url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id=61&search={sku}&mode=full"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("products"):
            p = data["products"][0]
            print(json.dumps(p, indent=2, ensure_ascii=False))
            return p
    return None

if __name__ == "__main__":
    find_product_details()

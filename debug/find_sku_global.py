import requests
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

SKU = "1053851_131"

def find_sku():
    accounts = [116, 61, 64, 63, 8]
    for acc_id in accounts:
        print(f"Searching for {SKU} in account {acc_id}...")
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc_id}&search={SKU}&mode=full"
        resp = requests.get(url, headers=GAPLI_HEADERS)
        if resp.status_code == 200:
            products = resp.json().get("products", [])
            if products:
                print(f"Found {len(products)} products in account {acc_id}")
                for p in products:
                    print(f"SKU: {p.get('sku')}, Name: {p.get('gapli_product_name')}")
                    desc = p.get('custom_description') or p.get('gapli_product_description') or ""
                    print(f"Desc: {desc}")
                    # print(json.dumps(p, indent=2, ensure_ascii=False))
            else:
                print("Not found.")
        else:
            print(f"Error: {resp.status_code}")

if __name__ == "__main__":
    find_sku()

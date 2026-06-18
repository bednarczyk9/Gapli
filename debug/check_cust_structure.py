import requests
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

def check():
    page = 1
    found = 0
    while page < 10:
        url = f"https://gapli.com/api/product-customizer/customizations-list?page={page}&limit=100"
        resp = requests.get(url, headers=GAPLI_HEADERS)
        items = resp.json().get('items', [])
        if not items: break
        for p in items:
            cp = p.get('custom_parameters')
            if cp and p['sku'] not in ["ND05_B26167-M_4069161993367_30", "3118-WI_307", "1053851_131"]:
                print(f"SKU: {p['sku']}")
                print("Content:", json.dumps(cp, indent=2))
                found += 1
                if found > 3: return
        page += 1


if __name__ == "__main__":
    check()

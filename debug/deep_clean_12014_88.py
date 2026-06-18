import requests
import time

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "12014_88"

def clean_sku():
    while True:
        url = f"https://gapli.com/api/product-customizer/customizations-list?sku={SKU}"
        resp = requests.get(url, headers=GAPLI_HEADERS).json()
        items = resp.get('items', [])
        print(f"Remaining customizations: {len(items)}")
        if not items:
            break
            
        # Delete by SKU - it seems to delete one each time
        del_url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro&konto_allegro_id=63"
        dr = requests.delete(del_url, headers=GAPLI_HEADERS)
        print(f"  Delete status: {dr.status_code}")
        time.sleep(1)

if __name__ == "__main__":
    clean_sku()

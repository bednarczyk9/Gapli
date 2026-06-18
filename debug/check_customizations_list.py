import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

def check_customizations():
    url = "https://gapli.com/api/product-customizer/customizations-list?limit=1000"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        items = resp.json().get("items", [])
        print(f"Total items in customizations-list: {len(items)}")
        for item in items:
            sku = item.get("sku")
            desc = item.get("custom_description") or ""
            if "Parasol" in desc:
                print(f"Found Parasol in customization for SKU: {sku}")
                print(f"Snippet: {desc[:100]}...")
    else:
        print(f"Error: {resp.status_code}")

if __name__ == "__main__":
    check_customizations()

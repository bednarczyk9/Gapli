import requests
import json
import os

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def get_cust():
    url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code == 200:
        data = resp.json().get("data", {})
        print("HTML length:", len(data.get("custom_description", "")))
        print("HTML content:")
        print(data.get("custom_description"))
        
        # Count tags
        html = data.get("custom_description", "")
        print("\nTag counts:")
        print(f"<b>: {html.lower().count('<b>')}")
        print(f"</b>: {html.lower().count('</b>')}")
        print(f"<p>: {html.lower().count('<p>')}")
        print(f"</p>: {html.lower().count('</p>')}")
    else:
        print(f"Error: {resp.status_code}")

if __name__ == "__main__":
    get_cust()

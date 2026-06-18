import requests
import json
import os
import sys

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = sys.argv[1] if len(sys.argv) > 1 else "12014_88"

def delete_duplicates():
    url = f"https://gapli.com/api/product-customizer/customizations-list?sku={SKU}&limit=100"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    
    items = resp.json().get("items", [])
    print(f"Found {len(items)} customizations for {SKU}.")
    
    if len(items) <= 1:
        print("No duplicates found.")
        return
        
    # Sort by ID or created_at to keep the newest
    items.sort(key=lambda x: int(x["id"]), reverse=True)
    
    to_keep = items[0]
    print(f"Keeping newest ID {to_keep['id']} (Created at: {to_keep.get('created_at')})")
    
    for i in items[1:]:
        cust_id = i["id"]
        print(f"Deleting duplicate ID {cust_id}...")
        del_url = f"https://gapli.com/api/product-customizer/customizations/{cust_id}"
        dr = requests.delete(del_url, headers=GAPLI_HEADERS)
        print(f"  Result: {dr.status_code}")

if __name__ == "__main__":
    delete_duplicates()

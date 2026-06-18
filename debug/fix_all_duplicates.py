import requests
import json
import os
import re
import time

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "1053851_131"

def fix_all_duplicates():
    url = f"https://gapli.com/api/product-customizer/customizations-list?sku={SKU}&limit=100"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    if resp.status_code != 200: return
    
    items = resp.json().get("items", [])
    print(f"Processing {len(items)} customizations for SKU {SKU}")
    
    fixed_count = 0
    
    for i in items:
        cust_id = i["id"]
        desc = i.get("custom_description", "")
        
        # Balance check
        open_b = desc.lower().count('<b>')
        close_b = desc.lower().count('</b>')
        
        if open_b != close_b or '<b></p>' in desc:
            print(f"Fixing ID {cust_id} (b-tags: {open_b}/{close_b})")
            
            # Simple balancing
            fixed_desc = desc.replace('.<b></p>', '.</b></p>').replace(').<b></p>', ').</b></p>').replace('zestawu.<b></p>', 'zestawu.</b></p>')
            
            # Re-count and force balance if still broken
            if fixed_desc.lower().count('<b>') > fixed_desc.lower().count('</b>'):
                 # Close all at the end
                 fixed_desc += "</b>" * (fixed_desc.lower().count('<b>') - fixed_desc.lower().count('</b>'))
            
            # Update specific ID
            # In Gapli, posting to /customizations updates the record for the SKU.
            # But we might need to delete duplicates.
            
            # Let's try to update using the base endpoint first.
            payload = i
            payload["custom_description"] = fixed_desc
            up_url = "https://gapli.com/api/product-customizer/customizations"
            up_resp = requests.post(up_url, headers=GAPLI_HEADERS, json=payload)
            print(f"  Update Result for {cust_id}: {up_resp.status_code}")
            fixed_count += 1
            
    print(f"Cleanup complete. Fixed {fixed_count} records.")
    
    # Final step: Trigger resync for account 63
    api_key = os.environ.get("Gapli_Apikey")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    r = requests.post("https://gapli.com/api/v1/integrations/marketplace/listing", headers=headers, json={
        "action": "send",
        "account_id": "63",
        "product_skus": [SKU]
    })
    print(f"Trigger result: {r.text}")

if __name__ == "__main__":
    fix_all_duplicates()

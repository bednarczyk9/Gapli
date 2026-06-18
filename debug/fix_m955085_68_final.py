import requests
import json
import re
import time

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_API_KEY = "gapli_ba90f561bf78bf55652e21b5ed33400b7551219e"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}
SKU = "M955085_68"

ACCOUNTS = ["61", "63", "64", "116"]

def fix():
    # 1. Fetch reference customization (from any account, they are SKU-based)
    ref_url = f"https://gapli.com/api/product-customizer/customizations?sku={SKU}&platform=allegro"
    resp = requests.get(ref_url, headers=GAPLI_HEADERS)
    if resp.status_code != 200:
        print(f"Failed to fetch reference customization: {resp.status_code}")
        return
    
    ref_data = resp.json().get("data")
    if not ref_data:
        print("No customization data found.")
        return

    # Clean the reference description once
    desc = ref_data.get("custom_description", "")
    
    def clean_html_for_allegro(html):
        # 1. Extract table data to text if present
        if "<table" in html:
            cells = re.findall(r'<td>(.*?)</td>', html, re.DOTALL)
            table_text = "Parametry: " + ", ".join([re.sub(r'<.*?>', '', c).strip() for c in cells])
            html = re.sub(r'<table.*?</table>', f" {table_text} ", html, flags=re.DOTALL)

        html = html.replace("<strong>", "<b>").replace("</strong>", "</b>")
        html = html.replace("<br>", "\n").replace("<br />", "\n").replace("<br/>", "\n")
        html = re.sub(r'</?(?!b|ul|li|/b|/ul|/li)[a-z0-9]+(?:\s+[^>]*)?>', ' ', html, flags=re.IGNORECASE)
        lines = [l.strip() for l in html.split("\n") if l.strip()]
        paragraphs = []
        for line in lines:
            open_b = len(re.findall(r'<b>', line, re.IGNORECASE))
            close_b = len(re.findall(r'</b>', line, re.IGNORECASE))
            if open_b > close_b: line += "</b>" * (open_b - close_b)
            elif close_b > open_b: line = re.sub(r'^(\s*</b>)+', '', line, flags=re.IGNORECASE)
            paragraphs.append(f"<p>{line}</p>")
        return "".join(paragraphs)

    final_desc = clean_html_for_allegro(desc)
    print(f"Final cleaned description for all: {final_desc}")

    for acc_id in ACCOUNTS:
        print(f"\n--- Processing Account {acc_id} ---")
        
        # 2. Save customization specifically for this SKU/Platform
        # (In Gapli, customizations are usually global per user per SKU, but we trigger per account)
        payload = {
            "sku": SKU,
            "scope": "user",
            "platform": "allegro",
            "custom_description": final_desc,
            "custom_parameters": {
                "Stan": "Nowy",
                "Kolor": "szary",
                "Marka": "bez marki",
                "Rozmiar": "L/XL",
                "EAN (GTIN)": "5904726003527"
            },
            "custom_name": "Koszula Nocna Ciążowa Model 0192 Grafit - PeeKaBoo",
            "is_active": True,
            "images_mode": "replace"
        }
        
        r_save = requests.post("https://gapli.com/api/product-customizer/customizations", headers=GAPLI_HEADERS, json=payload)
        print(f"Customization saved for {acc_id}: {r_save.status_code}")

        # 3. Find and Nuke product in this specific account
        search_url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={acc_id}&search={SKU}"
        resp_p = requests.get(search_url, headers=GAPLI_HEADERS)
        if resp_p.status_code == 200 and resp_p.json().get("products"):
            for prod in resp_p.json()["products"]:
                real_p_id = prod["id"]
                print(f"Found Product ID {real_p_id} on Acc {acc_id}. Nuking...")
                
                del_url = "https://gapli.com/api/products-manager/allegro/permanent-delete"
                del_payload = {
                    "mode": "selected",
                    "product_ids": [{"id": str(real_p_id), "konto_allegro_id": str(acc_id)}]
                }
                r_del = requests.delete(del_url, headers=GAPLI_HEADERS, json=del_payload)
                print(f"Delete Result: {r_del.status_code}")
        else:
            print(f"Product not found on Acc {acc_id}, skipping delete.")

        # 4. Trigger Sync
        time.sleep(2)
        send_url = "https://gapli.com/api/v1/integrations/marketplace/listing"
        send_headers = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Content-Type": "application/json"}
        send_payload = {
            "action": "send",
            "account_id": acc_id,
            "product_skus": [SKU],
            "force_update": True
        }
        r_send = requests.post(send_url, headers=send_headers, json=send_payload)
        print(f"Sync result for {acc_id}: {r_send.text}")

if __name__ == "__main__":
    fix()

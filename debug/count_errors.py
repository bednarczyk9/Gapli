import requests
import os

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": GAPLI_TOKEN}

ACCOUNTS = [61, 63, 64] # radosnydzieciak, skarbiec_ofert, hit_bazar
STATUSES = ["ERROR", "VALIDATION_ERROR"]

def count_errors():
    total_valid_errors = 0
    total_zero_stock_errors = 0
    
    for account_id in ACCOUNTS:
        for status in STATUSES:
            page = 1
            while True:
                url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={account_id}&status={status}&limit=100&page={page}"
                resp = requests.get(url, headers=HEADERS)
                if resp.status_code != 200:
                    break
                
                data = resp.json()
                products = data.get("products", [])
                
                for p in products:
                    stock = p.get("gapli_product_stock_quantity", 0)
                    if stock is None:
                        stock = 0
                        
                    if int(stock) > 0:
                        total_valid_errors += 1
                    else:
                        total_zero_stock_errors += 1
                
                if page >= data.get("totalPages", 1):
                    break
                page += 1

    print(f"Products to repair (Stock > 0): {total_valid_errors}")
    print(f"Products skipped (Stock == 0): {total_zero_stock_errors}")
    print(f"Total Errors: {total_valid_errors + total_zero_stock_errors}")

if __name__ == "__main__":
    count_errors()

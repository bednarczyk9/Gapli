import requests
import pandas as pd
import os
import logging
from datetime import datetime

# Gapli Token
TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"

def export_diverse():
    url = 'https://gapli.com/api/products-manager/products'
    all_cands = []
    page = 50 # Start from a later page to get different products
    
    print(f"Exporting diverse products starting from page {page}...")
    
    while len(all_cands) < 100:
        params = {'limit': 50, 'page': page}
        resp = requests.get(url, headers={'Authorization': TOKEN}, params=params).json()
        products = resp.get('products', [])
        if not products:
            break
            
        for p in products:
            if p.get('global_unique_id') and not p.get('allegro_blocked'):
                all_cands.append({
                    'SKU': p['sku'],
                    'EAN': p['global_unique_id'],
                    'Nazwa Produktu': p['name'],
                    'Cena Brutto (Gapli)': round(float(p.get('sale_net_price', 0)) * 1.23, 2)
                })
                if len(all_cands) >= 100:
                    break
        page += 1
        
    df = pd.DataFrame(all_cands)
    filename = 'gapli_potential_products_diverse.xlsx'
    df.to_excel(filename, index=False)
    print(f"Zapisano 100 różnorodnych produktów do pliku: {filename}")

if __name__ == "__main__":
    export_diverse()

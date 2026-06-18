import pandas as pd
import json

try:
    df = pd.read_excel("errors_aleja_okazji_20260606_083544.xlsx")
    print(f"Columns: {df.columns.tolist()}")
    print(df.head())
    
    # Identify SKU column
    sku_col = None
    for col in df.columns:
        if 'sku' in col.lower():
            sku_col = col
            break
            
    if sku_col:
        # Check first 100 characters of descriptions
        df['desc_prefix'] = df['allegro_offer_description'].astype(str).str[:100]
        prefixes = df['desc_prefix'].unique()
        print(f"Unique description prefixes in Excel ({len(prefixes)}):")
        for p in prefixes[:20]:
            print(f"- {p}")
        print(f"Total unique SKUs in error file: {len(skus)}")
        with open("error_skus.json", "w") as f:
            json.dump(skus, f)
    else:
        print("No SKU column found.")
except Exception as e:
    print(f"Error reading excel: {e}")

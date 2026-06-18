import pandas as pd
import json

df = pd.read_excel("errors_aleja_okazji_20260606_083544.xlsx")
search_str = "Parasol Ogrodowy"

found = []
for index, row in df.iterrows():
    api_resp = str(row.get('allegro_api_response', ''))
    if search_str in api_resp:
        found.append({
            "sku": row['sku'],
            "api_response_snippet": api_resp[:500]
        })

print(f"Total found in allegro_api_response: {len(found)}")
if found:
    print(json.dumps(found[:5], indent=2, ensure_ascii=False))

import json

with open("all_products_descriptions_61.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for p in data:
    if p['sku'] == "1053851_131":
        print(json.dumps(p, indent=2, ensure_ascii=False))
        break

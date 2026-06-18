import json

with open("all_products_descriptions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

found_count = 0
for p in data:
    if p['sku'] == "1053851_131":
        continue
        
    s = json.dumps(p)
    if "Parasol" in s:
        found_count += 1
        if found_count <= 5:
            print(f"SKU: {p['sku']}, Name: {p['name']}")

print(f"Total products with 'Parasol' in JSON: {found_count}")

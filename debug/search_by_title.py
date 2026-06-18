import json

search_str = "PARASOL OGRODOWY Z OŚWIETLENIEM LED 300CM"
found = []

for filename in ["all_products_descriptions.json", "all_products_descriptions_61.json"]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            for p in data:
                if p['sku'] == "1053851_131": continue
                
                name = p.get('name') or ""
                if search_str.upper() in name.upper():
                    found.append(p)
    except: pass

print(f"Total found by title: {len(found)}")
if found:
    for p in found:
        print(f"SKU: {p['sku']}, Name: {p['name']}")

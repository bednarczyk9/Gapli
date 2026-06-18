import json

search_str = "Parasol ogrodowy o średnicy 300 cm z wbudowanym oświetleniem"
found = []

for filename in ["all_products_descriptions.json", "all_products_descriptions_61.json"]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            for p in data:
                if p['sku'] == "1053851_131": continue
                
                s = json.dumps(p)
                if search_str in s:
                    found.append(p)
    except: pass

print(f"Total found: {len(found)}")
if found:
    for p in found[:5]:
        print(f"SKU: {p['sku']}, Name: {p['name']}")

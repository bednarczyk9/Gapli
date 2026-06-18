import json

search_str = "Lubisz spędzać czas na świeżym powietrzu"
found = []

for filename in ["all_products_descriptions.json", "all_products_descriptions_61.json"]:
    print(f"Searching in {filename}...")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            for p in data:
                if p['sku'] == "1053851_131":
                    continue
                
                # Check all fields
                fields = ['offer_desc', 'custom_desc', 'gapli_desc']
                for field in fields:
                    val = p.get(field)
                    if val and search_str in val:
                        found.append({
                            "sku": p['sku'],
                            "name": p['name'],
                            "found_in": field,
                            "filename": filename
                        })
                        break
    except Exception as e:
        print(f"Error reading {filename}: {e}")

print(f"Total found: {len(found)}")
if found:
    print(json.dumps(found[:20], indent=2, ensure_ascii=False))

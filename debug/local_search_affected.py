import json

search_str = "Lubisz spędzać czas na świeżym powietrzu"
with open("all_products_descriptions.json", "r", encoding="utf-8") as f:
    data = json.load(f)
# ... search ...
with open("all_products_descriptions_61.json", "r", encoding="utf-8") as f:
    data61 = json.load(f)
# ... search ...
found = []
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
                "snippet": val[:200]
            })
            break

print(f"Total found: {len(found)}")
if found:
    print(json.dumps(found[:10], indent=2, ensure_ascii=False))

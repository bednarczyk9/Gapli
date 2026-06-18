import json

with open("all_products_descriptions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for i in range(min(5, len(data))):
    p = data[i]
    print(f"SKU: {p['sku']}")
    print(f"Name: {p['name']}")
    print(f"Offer Desc: {p['offer_desc'][:50] if p['offer_desc'] else 'None'}")
    print(f"Gapli Desc: {p['gapli_desc'][:50] if p['gapli_desc'] else 'None'}")
    print("-" * 20)

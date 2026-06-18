import requests

token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE'
headers = {'Authorization': token}

r = requests.get('https://gapli.com/api/products-manager/allegro/products?search=AGDADLWYC0009_33&mode=full', headers=headers)
products = r.json().get('products', [])

if products:
    prod = products[0]
    
    # Check GAPLI base product EAN
    print("Gapli Base Unique ID:", repr(prod.get('gapli_product_global_unique_id')))
    
    # Check Catalog Parameters EAN
    cat_params = prod.get('allegro_catalog_parameters', [])
    if cat_params:
        ean_from_catalog = [p['values'][0] for p in cat_params if isinstance(p, dict) and p.get('name') == 'EAN (GTIN)' and p.get('values')]
        print('Catalog EAN (values):', repr(ean_from_catalog[0]) if ean_from_catalog else 'N/A')
        
        ean_labels = [p['valuesLabels'][0] for p in cat_params if isinstance(p, dict) and p.get('name') == 'EAN (GTIN)' and p.get('valuesLabels')]
        print('Catalog EAN (labels):', repr(ean_labels[0]) if ean_labels else 'N/A')
        
    print("\nFull product parameters info:")
    for p in cat_params:
        if isinstance(p, dict):
            print(f"{p.get('name')}: {p.get('values')} (Labels: {p.get('valuesLabels')})")
        else:
            print(f"Unknown param format: {p}")
else:
    print("Product not found")

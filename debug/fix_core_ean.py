import requests

token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE'
headers = {'Authorization': token, 'Content-Type': 'application/json'}
sku = 'AGDADLWYC0009_33'
correct_ean = '5902934830577'

r = requests.get(f'https://gapli.com/api/products-manager/allegro/products?search={sku}&mode=full', headers=headers)
products = r.json().get('products', [])

for prod in products:
    p_id = prod['id']
    print(f"Fixing core data for Product ID {p_id} (Account {prod['konto_allegro_id']})")
    
    cat_params = prod.get('allegro_catalog_parameters', [])
    modified = False
    
    for param in cat_params:
        if isinstance(param, dict) and param.get('id') == '225693': # EAN ID
            old_val = param.get('values', [])
            print(f"Found EAN param. Old values: {old_val}")
            param['values'] = [correct_ean]
            modified = True
            
    payload = {}
    if modified:
        payload['allegro_catalog_parameters'] = cat_params
        
    if prod.get('gapli_product_global_unique_id') != correct_ean:
        print(f"Fixing global_unique_id from {prod.get('gapli_product_global_unique_id')} to {correct_ean}")
        payload['gapli_product_global_unique_id'] = correct_ean
        
    if payload:
        patch_r = requests.patch(f'https://gapli.com/api/products-manager/allegro/products/{p_id}', headers=headers, json=payload)
        print(f"PATCH result ({patch_r.status_code}): {patch_r.text[:100]}")
    else:
        print("No core data modification needed.")

import requests

token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE'
headers = {'Authorization': token, 'Content-Type': 'application/json'}
sku = 'AGDADLWYC0009_33'
api_key = 'gapli_ba90f561bf78bf55652e21b5ed33400b7551219e'

print(f"Fetching customization for {sku}...")
r = requests.get(f'https://gapli.com/api/product-customizer/customizations?sku={sku}&platform=allegro', headers=headers)
if r.status_code == 200:
    cust = r.json().get('data')
    if cust:
        params = cust.get('custom_parameters', {})
        
        # Add the ID as a key to see if Gapli parses it better
        # 225693 is EAN
        params['225693'] = '5902934830577'
        params['EAN (GTIN)'] = '5902934830577'
        # Just in case
        params['EAN'] = '5902934830577'
        
        print(f"New params: {params}")
        
        payload = {
            'sku': sku,
            'scope': 'user',
            'platform': 'allegro',
            'custom_name': cust['custom_name'],
            'custom_description': cust['custom_description'],
            'custom_parameters': params,
            'is_active': True
        }
        
        r2 = requests.post('https://gapli.com/api/product-customizer/customizations', headers=headers, json=payload)
        print(f"Update Customization Result ({r2.status_code}): {r2.text[:200]}")
        
        # Now trigger send
        print("Triggering send...")
        send_headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        send_payload = {'action': 'send', 'account_id': '61', 'product_skus': [sku], 'force_update': True}
        r3 = requests.post('https://gapli.com/api/v1/integrations/marketplace/listing', headers=send_headers, json=send_payload)
        print(f"Send Result ({r3.status_code}): {r3.text}")
    else:
        print("No customization found.")
else:
    print(f"Error fetching: {r.status_code}")

import requests
import json

token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE'
headers = {'Authorization': token, 'Content-Type': 'application/json'}
sku = '12014_88'

print(f"Fetching customization for {sku}...")
r = requests.get(f'https://gapli.com/api/product-customizer/customizations?sku={sku}&platform=allegro', headers=headers)
if r.status_code == 200:
    cust = r.json().get('data')
    if cust:
        params = cust.get('custom_parameters', {})
        print(f"Original params: {params}")
        
        # FIX PARAMS
        params['Waga produktu z opakowaniem jednostkowym'] = '3'
        if 'Wysokość' in params:
            del params['Wysokość']
        
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
        print(f"Update Result ({r2.status_code}): {r2.text}")
    else:
        print("No customization found.")
else:
    print(f"Error fetching: {r.status_code} {r.text}")

import requests
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"

url = 'https://gapli.com/api/products-manager/products'
headers = {'Authorization': GAPLI_TOKEN}

try:
    resp = requests.get(url, headers=headers, params={'limit': 10})
    print(f"Status: {resp.status_code}")
    data = resp.json()
    products = data.get('products', [])
    if products:
        print(f"Pobrano {len(products)} produktów.")
        print(json.dumps(products[0], indent=2))
    else:
        print("Brak produktów w odpowiedzi:", data)
except Exception as e:
    print(f"Błąd: {e}")

import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE'
headers = {'Authorization': token}
r = requests.get('https://gapli.com/api/products-manager/allegro/products?search=M955085_68', headers=headers)
for p in r.json().get('products', []):
    print(f"{p['store_name']} (ID {p['konto_allegro_id']}): {p.get('allegro_sync_upload_error_message', p.get('allegro_sync_upload_status'))}")

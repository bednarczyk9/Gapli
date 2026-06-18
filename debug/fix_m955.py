import os
import sys
import logging
import requests

sys.path.append(os.getcwd())
from pipeline.repair_missing_descriptions import repair_missing_description, get_allegro_token

logging.basicConfig(level=logging.INFO)

def fix_m9():
    client_id = os.environ.get("skarbiec_client_id")
    client_secret = os.environ.get("skarbiec_client_secret")
    token = get_allegro_token(client_id, client_secret)
    
    # Get product data from gapli
    gapli_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
    headers = {"Authorization": gapli_token}
    r = requests.get('https://gapli.com/api/products-manager/allegro/products?search=M955085_68&konto_allegro_id=63&mode=full', headers=headers)
    
    products = r.json().get("products", [])
    if products:
        print("Executing repair for:", products[0]['sku'])
        repair_missing_description(products[0], token)
    else:
        print("Product not found.")

if __name__ == "__main__":
    fix_m9()

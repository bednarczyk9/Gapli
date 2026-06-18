import requests
import os

API_KEY = os.environ.get("Gapli_Apikey")
headers = {"Authorization": f"Bearer {API_KEY}"}

def find_price(target_price):
    url = "https://gapli.com/api/v1/integrations/marketplace/products"
    offset = 0
    limit = 100
    
    print(f"Searching for price {target_price}...")
    
    while offset < 5000: # Search first 5000 products
        params = {"limit": limit, "offset": offset, "status": "active"}
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            break
            
        products = resp.json().get("products", [])
        if not products:
            break
            
        for p in products:
            price = float(p.get("price", 0))
            if abs(price - target_price) < 0.01:
                print(f"FOUND! SKU: {p['sku']} | Price: {p['price']} | Account: {p['allegro_login']} | Name: {p['name']}")
                
        offset += limit
    print("Search finished.")

if __name__ == "__main__":
    find_price(1600.54)
    find_price(1162.79)

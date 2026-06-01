import requests
import os

API_KEY = os.environ.get("Gapli_Apikey")
headers = {"Authorization": f"Bearer {API_KEY}"}

def find_specific_skus():
    url = "https://gapli.com/api/v1/integrations/marketplace/products"
    offset = 0
    limit = 100
    target_skus = ['180800_134', '700_152']
    found_count = 0
    
    print(f"Searching for SKUs: {target_skus}")
    
    while offset < 10000: # Search first 10k products
        params = {"limit": limit, "offset": offset, "status": "active"}
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print(f"Error at offset {offset}: {resp.status_code}")
            break
            
        products = resp.json().get("products", [])
        if not products:
            break
            
        for p in products:
            if p['sku'] in target_skus:
                print(f"FOUND! SKU: {p['sku']} | Price: {p['price']} | Account: {p['allegro_login']} | Name: {p['name']}")
                found_count += 1
                
        if found_count >= len(target_skus) * 2: # Stop after finding a few instances
             break
                
        offset += limit
    print("Search finished.")

if __name__ == "__main__":
    find_specific_skus()

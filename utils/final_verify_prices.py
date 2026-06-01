import requests
import os

API_KEY = os.environ.get("Gapli_Apikey")
headers = {"Authorization": f"Bearer {API_KEY}"}

def check(sku):
    url = "https://gapli.com/api/v1/integrations/marketplace/products"
    params = {"sku": sku}
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        if products:
            p = products[0]
            print(f"SKU: {p['sku']} | Price: {p['price']} | Name: {p['name'][:50]}")
        else:
            print(f"SKU: {sku} not found in V1 API")
    else:
        print(f"Error for {sku}: {resp.status_code}")

if __name__ == "__main__":
    check("180800_134")
    check("700_152")

import requests
import os
import json
import time

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}
ACCOUNT_ID = 116

def fetch_all_skus():
    skus = []
    limit = 1000
    offset = 0
    
    print(f"Fetching all SKUs for account {ACCOUNT_ID}...")
    
    while True:
        url = f"https://gapli.com/api/v1/integrations/marketplace/products?account_id={ACCOUNT_ID}&limit={limit}&offset={offset}"
        resp = requests.get(url, headers=HEADERS)
        
        if resp.status_code != 200:
            print(f"Error fetching products at offset {offset}: {resp.status_code}")
            break
            
        data = resp.json()
        products = data.get("products", [])
        if not products:
            break
            
        page_skus = [p.get("sku") for p in products if p.get("sku")]
        skus.extend(page_skus)
        print(f"Fetched {len(skus)} SKUs so far...")
        
        if not data.get("pagination", {}).get("has_more"):
            break
            
        offset += limit
        time.sleep(0.5)
        
    return skus

def bulk_remove_skus(skus):
    if not skus:
        print("No SKUs to remove.")
        return
        
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    
    # Process in batches of 100
    batch_size = 100
    success_count = 0
    
    print(f"Starting bulk removal of {len(skus)} SKUs...")
    
    for i in range(0, len(skus), batch_size):
        batch = skus[i:i+batch_size]
        body = {
            "action": "remove",
            "account_id": str(ACCOUNT_ID),
            "product_skus": batch
        }
        
        resp = requests.post(url, headers=HEADERS, json=body)
        if resp.status_code in [200, 201, 204]:
            success_count += len(batch)
            print(f"Removed {success_count}/{len(skus)} SKUs...")
        else:
            print(f"Failed batch {i//batch_size}: {resp.status_code} {resp.text}")
            
        time.sleep(1)

if __name__ == "__main__":
    # FIRST, let's just fetch and save the list to be safe
    all_skus = fetch_all_skus()
    with open("skus_to_remove_116.json", "w") as f:
        json.dump(all_skus, f)
    print(f"Total SKUs found: {len(all_skus)}")
    
    # ASK USER BEFORE REMOVING
    print("\nREADY TO REMOVE. Run with --confirm to execute.")
    import sys
    if "--confirm" in sys.argv:
        bulk_remove_skus(all_skus)

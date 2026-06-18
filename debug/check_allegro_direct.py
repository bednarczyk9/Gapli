import requests
import json
import base64
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AlejaOkazji Credentials
CLIENT_ID = "429dd510a6714131bcc6359602f5df56"
CLIENT_SECRET = "U9uFj24fhXBXF1aSSfds2pgISUsvgKtxIRhel0RQu5tOBOFLjbgGOR8OAiA02aRe"

# Gapli Data
GAPLI_DATA_FILE = "all_products_descriptions.json"
BAD_STRING = "Parasol Ogrodowy"

def get_allegro_token():
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    url = "https://allegro.pl/auth/oauth/token?grant_type=client_credentials"
    headers = {"Authorization": f"Basic {auth_header}"}
    resp = requests.post(url, headers=headers)
    return resp.json().get("access_token") if resp.status_code == 200 else None

def check_allegro_offers():
    token = get_allegro_token()
    if not token: return

    a_headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }

    # Get Seller ID
    # me_resp = requests.get("https://api.allegro.pl/me", headers=a_headers)
    # seller_id = me_resp.json().get("id")
    # Actually, AlejaOkazji seller_id can be found from public link or I can just list my own offers if I had authorization_code.
    # Since I only have client_credentials, I can only search PUBLIC offers.
    
    seller_login = "skarbiec_ofert"
    
    affected = []
    
    # Search for offers by this seller with keyword "Parasol"
    # Wait, if I search for "Parasol" by this seller, I'll find actual parasols too.
    # But I can check their descriptions.
    
    url = f"https://api.allegro.pl/offers/listing?seller.login={seller_login}&phrase={BAD_STRING}"
    resp = requests.get(url, headers=a_headers)
    if resp.status_code == 200:
        items = resp.json().get("items", {}).get("regular", [])
        print(f"Found {len(items)} offers for seller {seller_login} with phrase '{BAD_STRING}'")
        for item in items:
            offer_id = item.get("id")
            title = item.get("name")
            print(f"Checking {offer_id}: {title}")
            
            # Now I need the description. description is NOT in listing.
            # I need GET /sale/product-offers/{offerId}
            # BUT product-offers endpoint REQUIRES authorization_code (private scope).
            # Listing endpoint only gives public data.
            
            # Wait! Can I get the description from the public offer page?
            # Yes, via web scraping or a different public endpoint if exists.
            
            # Actually, I can use the Gapli API to fetch the product by offer_id!
            # And Gapli HAS the authorization to fetch its own offers.
            
    return []

if __name__ == "__main__":
    affected = check_allegro_offers()
    logger.info(f"Total affected found directly on Allegro: {len(affected)}")
    with open("affected_direct_allegro.json", "w", encoding="utf-8") as f:
        json.dump(affected, f, indent=4, ensure_ascii=False)

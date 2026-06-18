import requests
import os
import json

GAPLI_API_KEY = os.environ.get("Gapli_Apikey")
HEADERS = {"Authorization": f"Bearer {GAPLI_API_KEY}", "Accept": "application/json"}

def list_actions():
    url = "https://gapli.com/api/v1/integrations/marketplace/listing"
    # Sending empty body to see if it lists supported actions or gives schema
    resp = requests.options(url, headers=HEADERS)
    print(f"OPTIONS Status: {resp.status_code}")
    print(f"Allow: {resp.headers.get('Allow')}")
    
    # Try invalid action to see error message with supported actions
    body = {"action": "list_supported_actions", "account_id": "116"}
    resp = requests.post(url, headers=HEADERS, json=body)
    print(f"POST Status: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    list_actions()

import os
import requests
import json
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

api_key = os.environ.get("Gapli_Apikey")
if not api_key:
    print("Gapli_Apikey not found")
    exit(1)

if not api_key.startswith("Bearer "):
    headers = {"Authorization": f"Bearer {api_key}"}
else:
    headers = {"Authorization": api_key}

base_url = "https://gapli.com/api/v1/integrations"

def get_accounts():
    url = f"{base_url}/marketplace/accounts"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("accounts", [])

try:
    accounts = get_accounts()
    print("Available marketplace accounts:")
    for acc in accounts:
        print(f"- {acc.get('store_name')} (ID: {acc.get('id')}, Platform: {acc.get('platform')})")
except Exception as e:
    print(f"Error: {e}")

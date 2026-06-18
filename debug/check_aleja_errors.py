import os
import requests
import json
import logging
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_token():
    # Hardcoded token from other scripts
    return "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"

def check_accounts(token):
    headers = {"Authorization": token, "Accept": "application/json"}
    url = "https://gapli.com/api/products-manager/allegro/accounts"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        accounts = resp.json().get("accounts", [])
        for acc in accounts:
            logger.info(f"Account: {acc.get('store_name')} (ID: {acc.get('id')}, Platform: {acc.get('platform')})")
        return accounts
    else:
        logger.error(f"Failed to fetch accounts: {resp.status_code} {resp.text}")
        return []

def check_product_errors(token, account_id):
    headers = {"Authorization": token, "Accept": "application/json"}
    
    statuses = ["ACTIVE", "INACTIVE", "ERROR", "VALIDATION_ERROR", "DRAFT"]
    
    for status in statuses:
        logger.info(f"--- Status: {status} ---")
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={account_id}&status={status}&limit=50&mode=full"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            total = data.get("total", 0)
            products = data.get("products", [])
            logger.info(f"Total reported: {total}. Showing first {len(products)}:")
            
            real_active_count = 0
            for p in products:
                sku = p.get('sku')
                offer_id = p.get('allegro_offer_id')
                offer_status = p.get('allegro_offer_status')
                sync_msg = p.get('allegro_sync_upload_error_message') or p.get('allegro_sync_publication_error_message')
                api_resp = p.get('allegro_api_response') or {}
                api_err = json.dumps(api_resp.get('errors')) if isinstance(api_resp, dict) else "N/A"
                
                if offer_id:
                    real_active_count += 1
                
                if real_active_count <= 5 or offer_id: # Log first 5 or any that have an ID
                    logger.info(f"  SKU: {sku} | OfferID: {offer_id} | OfferStatus: {offer_status} | SyncMsg: {sync_msg} | APIErr: {api_err}")
            
            logger.info(f"Summary for {status}: {real_active_count}/{len(products)} on first page have an OfferID.")
        else:
            logger.error(f"Failed to fetch {status}: {resp.status_code}")

if __name__ == "__main__":
    token = get_token()
    if not token:
        logger.error("No token found. Please set Gapli_Apikey.")
    else:
        accounts = check_accounts(token)
        aleja = next((acc for acc in accounts if "AlejaOkazji" in acc.get('store_name')), None)
        if aleja:
            check_product_errors(token, aleja['id'])
        else:
            logger.warning("AlejaOkazji account not found.")

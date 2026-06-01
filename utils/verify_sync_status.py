import requests
import json
import logging
import pandas as pd
import os

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}
ACCOUNT_ID = "61"

def verify_sync_status(report_filename):
    report_path = os.path.join("reports", report_filename)
    if not os.path.exists(report_path):
        logger.error(f"Report file {report_path} not found.")
        return

    logger.info(f"Reading SKUs from {report_path}...")
    df_report = pd.read_excel(report_path)
    skus = df_report['sku'].tolist()
    
    results = []
    
    for sku in skus:
        logger.info(f"Checking status for {sku}...")
        url = f"https://gapli.com/api/products-manager/allegro/products?konto_allegro_id={ACCOUNT_ID}&search={sku}&mode=full"
        try:
            resp = requests.get(url, headers=HEADERS)
            if resp.status_code == 200:
                data = resp.json()
                products = data.get("products", [])
                if products:
                    p = products[0]
                    status = p.get("allegro_sync_upload_status")
                    error = p.get("allegro_sync_upload_error_message") or p.get("allegro_sync_upload_error_code")
                    last_attempt = p.get("allegro_sync_upload_last_attempt_at")
                    succeeded_at = p.get("allegro_sync_upload_succeeded_at")
                    
                    results.append({
                        "sku": sku,
                        "sync_status": status,
                        "error_message": error,
                        "last_attempt": last_attempt,
                        "succeeded_at": succeeded_at
                    })
                else:
                    results.append({"sku": sku, "sync_status": "NOT_FOUND"})
            else:
                results.append({"sku": sku, "sync_status": f"API_ERROR_{resp.status_code}"})
        except Exception as e:
            results.append({"sku": sku, "sync_status": "EXCEPTION", "error_message": str(e)})

    # Summary
    df_status = pd.DataFrame(results)
    print("\n--- SYNC STATUS SUMMARY ---")
    print(df_status[['sku', 'sync_status', 'error_message']].to_string(index=False))
    
    output_path = os.path.join("reports", f"sync_verification_{report_filename}")
    df_status.to_excel(output_path, index=False)
    logger.info(f"Verification report saved to {output_path}")

if __name__ == "__main__":
    verify_sync_status("ai_report_20260531_201325.xlsx")

import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": TOKEN, "Accept": "application/json"}

def ghost_buster_cleanup():
    sku = "1004260-660_150"
    # These IDs were captured from the corrupted customization-list
    ghost_ids = [172, 171, 170, 169, 168, 167, 166, 141, 142, 163, 162, 128, 129, 140, 125, 124, 152, 145, 143]
    
    logger.info(f"GhostBuster: Attempting to delete {len(ghost_ids)} hidden customizations for SKU {sku}...")
    
    for gid in ghost_ids:
        # Try both endpoints again with more aggressive headers
        del_url = f"https://gapli.com/api/product-customizer/customizations/{gid}"
        r = requests.delete(del_url, headers=HEADERS)
        logger.info(f"  Deleting ID {gid}: Status {r.status_code}")
        
    # Final check
    time.sleep(2)
    check_url = f"https://gapli.com/api/product-customizer/customizations-list?sku={sku}"
    v = requests.get(check_url, headers=HEADERS).json()
    logger.info(f"Remaining items after GhostBuster: {v.get('total', 0)}")

if __name__ == "__main__":
    ghost_buster_cleanup()

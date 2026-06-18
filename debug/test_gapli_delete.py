import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
HEADERS = {"Authorization": GAPLI_TOKEN, "Accept": "application/json"}

def test_delete_product(p_id):
    url = f"https://gapli.com/api/products-manager/allegro/products/{p_id}"
    logger.info(f"Attempting to DELETE product {p_id} at {url}")
    resp = requests.delete(url, headers=HEADERS)
    logger.info(f"Response: {resp.status_code} {resp.text}")
    return resp.status_code

if __name__ == "__main__":
    # Testing with SKU: GUHCP14XP4TDSCPB_81 (ID: 4652818)
    test_delete_product("4652818")

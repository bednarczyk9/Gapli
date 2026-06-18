import requests
import json

GAPLI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjksInVzZXJuYW1lIjoibWFyaWFhY3dpa2xhIiwiZW1haWwiOiJtYXJpYWFjd2lrbGFAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODAxNTI3NjksImV4cCI6MTc4MTM2MjM2OX0.FC4kPswLbAAltdpzm_EYbnU4uaq-zbA8f33GmD1HkXE"
GAPLI_HEADERS = {"Authorization": GAPLI_TOKEN, "Content-Type": "application/json"}

def check():
    url = f"https://gapli.com/api/product-customizer/customizations?sku=ND05_B26167-M_4069161993367_30&platform=allegro"
    resp = requests.get(url, headers=GAPLI_HEADERS)
    data = resp.json().get('data', {})
    print(data.get('custom_parameters'))


if __name__ == "__main__":
    check()

import json
import os
import base64

TOKEN_FILE = "allegro_token.json"

def inspect_token_file():
    if not os.path.exists(TOKEN_FILE):
        print("Token file not found.")
        return
    
    with open(TOKEN_FILE, "r") as f:
        tokens = json.load(f)
    
    access_token = tokens.get("access_token")
    if access_token:
        payload = access_token.split('.')[1]
        payload += '=' * (4 - len(payload) % 4)
        data = json.loads(base64.b64decode(payload))
        print(f"File contains token for user: {data.get('user_name')}")
        print(f"Client ID: {data.get('client_id')}")
    else:
        print("No access_token in file.")

if __name__ == "__main__":
    inspect_token_file()

import requests
import json
import os
import base64

# From debug/direct_allegro_update_refresh.py
REFRESH_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2FsbGVncm8ucGwiLCJ1c2VyX25hbWUiOiIxMTg0MjM5ODAiLCJzY29wZSI6WyJhbGxlZ3JvOmFwaTpvcmRlcnM6cmVhZCIsImFsbGVncm86YXBpOmZ1bGZpbGxtZW50OnJlYWQiLCJhbGxlZ3JvOmFwaTpwcm9maWxlOndyaXRlIiwiYWxsZWdybzphcGk6c2FsZTpvZmZlcnM6d3JpdGUiLCJhbGxlZ3JvOmFwaTpmdWxmaWxsbWVudDp3cml0ZSIsImFsbGVncm86YXBpOmJpbGxpbmc6cmVhZCIsImFsbGVncm86YXBpOmNhbXBhaWducyIsImFsbGVncm86YXBpOmRpc3B1dGVzIiwiYWxsZWdybzphcGk6YWZmaWxpYXRlOndyaXRlIiwiYWxsZWdybzphcGk6c2FsZTpvZmZlcnM6cmVhZCIsImFsbGVncm86YXBpOmJpZHMiLCJhbGxlZ3JvOmFwaTpzaGlwbWVudHM6d3JpdGUiLCJhbGxlZ3JvOmFwaTpvcmRlcnM6d3JpdGUiLCJhbGxlZ3JvOmFwaTphZHMiLCJhbGxlZ3JvOmFwaTpwYXltZW50czp3cml0ZSIsImFsbGVncm86YXBpOnNhbGU6c2V0dGluZ3M6d3JpdGUiLCJhbGxlZ3JvOmFwaTpwcm9maWxlOnJlYWQiLCJhbGxlZ3JvOmFwaTpyYXRpbmdzIiwiYWxsZWdybzphcGk6YWZmaWxpYXRlOnJlYWQiLCJhbGxlZ3JvOmFwaTpzYWxlOnNldHRpbmdzOnJlYWQiLCJhbGxlZ3JvOmFwaTpwYXltZW50czpyZWFkIiwiYWxsZWdybzphcGk6c2hpcG1lbnRzOnJlYWQiLCJhbGxlZ3JvOmFwaTptZXNzYWdpbmciXSwiYXRpIjoiMzY4ODQwNmQtNjYyMS00NDQ2LTk3MWMtOWIzZjY0ZTE1NjdiIiwiYWxsZWdyb19hcGkiOnRydWUsImV4cCI6MTc4ODU2MDY3NywiY2xpZW50X2lkIjoiNWI2ZTc4MWZmZjJhNDY0NmI4ZDE4ODU2MDdmMWZhOWUiLCJqdGkiOiIzZGY2MjliMi04YWVmLTQ3NTQtYjhiYS02ZjcwZjY5NTA4NmMifQ.fEbPN08j7-3BVNemcFcuSYMo1vKOs-EdwLZFQTl9I5TRo8EHJbUz-ExNXyn5cZARxO911CJHbmTgNYhVxz1yj8GjifC4qRZN_wbOGpVMd3MdEjR4btKnX9GQVqCvnbe066BPbAZ2qhfA6iKbhZ36ppiBbI190Sh-c5NVlSZvj6WHLwwkwP7UxUnZ5REfwXcxoUNW2ECSnT9UaxbfPpSVovRMPbxLCsqbMwSIXnLW3kpRn_6gy-ywRvRKT67Y7onOnnC098hAwqtSxg3p9GAtxvfXgvQYpT2M2Xzz_qH6zTozREWwizwzFemMc-MwtB7IJD9Yom6VVT4XTc-B2rJiBw"

# We need the client_id/secret for 5b6e781fff2a4646b8d1885607f1fa9e
# Let's search for this client_id again, maybe I missed it.

def check_refresh():
    # If I don't have the secret, I can't refresh.
    # But wait, maybe it's in the .env or some other file.
    pass

if __name__ == "__main__":
    # Decoding JWT to see more info
    import base64
    payload = REFRESH_TOKEN.split('.')[1]
    # fix padding
    payload += '=' * (4 - len(payload) % 4)
    import json
    data = json.loads(base64.b64decode(payload))
    print(f"Token belongs to user_name (ID): {data.get('user_name')}")
    print(f"Client ID: {data.get('client_id')}")

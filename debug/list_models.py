import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
resp = requests.get(url)
print(resp.status_code)
for m in resp.json().get('models', []):
    if 'gemini' in m['name']:
        print(m['name'], m.get('supportedGenerationMethods'))

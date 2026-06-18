import json
import re

def extract_next_data():
    file_path = "debug_manual_session_sku.html"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', content)
        if match:
            data = json.loads(match.group(1))
            with open("next_data_dump.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Extracted __NEXT_DATA__ to next_data_dump.json")
            
            # Look for tokens
            # Search recursively in the dict
            def find_keys(d, key_pat):
                results = []
                if isinstance(d, dict):
                    for k, v in d.items():
                        if re.search(key_pat, k, re.I):
                            results.append((k, v))
                        results.extend(find_keys(v, key_pat))
                elif isinstance(d, list):
                    for item in d:
                        results.extend(find_keys(item, key_pat))
                return results
            
            tokens = find_keys(data, "token|jwt|auth|session")
            for k, v in tokens:
                print(f"Found {k}: {str(v)[:50]}...")
        else:
            print("__NEXT_DATA__ not found in file.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_next_data()

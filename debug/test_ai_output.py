import json
from pipeline.repair_products_full import rewrite_with_gemini

# Test Gemini output structure
mandatory = [
    {'id': '123', 'name': 'Stan', 'type': 'dictionary', 'dictionary': ['Nowy', 'Używany']}
]
res = rewrite_with_gemini("Test", "Test desc", mandatory)
print(json.dumps(res, indent=2))

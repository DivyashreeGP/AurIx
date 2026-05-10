import requests
import json

# Test the /analyze endpoint
code = """import os
os.system('ls -la')
"""

try:
    resp = requests.post('http://localhost:8000/analyze', json={'code': code}, timeout=10)
    print("Status:", resp.status_code)
    print("Response:", json.dumps(resp.json(), indent=2)[:1000])
except Exception as e:
    print("Error:", e)
import requests
import json

# Test the /analyze-with-ai endpoint
code = """import os
os.system('ls -la')
"""

issues = [
    {"type": "OS-SYSTEM-002", "description": "os.system('ls -la')", "line": 2}
]

try:
    resp = requests.post('http://localhost:8000/analyze-with-ai', 
                        json={'code': code, 'issues': issues}, 
                        timeout=30)
    print("Status:", resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        print("Keys:", list(data.keys()))
        if 'source' in data:
            print("Source:", data['source'])
        if 'analysis' in data:
            print("Analysis:", data['analysis'][:200] if data['analysis'] else "Empty")
        if 'secure_code' in data:
            print("Secure Code:", repr(data['secure_code'][:300]) if data['secure_code'] else "Empty")
    else:
        print("Error Status:", resp.status_code)
        print("Error Response:", resp.text)
except Exception as e:
    print("Error:", e)
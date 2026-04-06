#!/usr/bin/env python3
"""Direct backend test to see exact response"""
import requests
import json

code = """import pickle
data = request.args.get('x')
obj = pickle.loads(data)"""

print("Testing backend /analyze endpoint...")
resp1 = requests.post('http://localhost:8000/analyze', json={'code': code})
issues = resp1.json().get('issues', [])
print(f"Issues: {json.dumps(issues, indent=2)}\n")

print("Testing backend /analyze-with-ai endpoint...")
resp2 = requests.post('http://localhost:8000/analyze-with-ai', 
                     json={'code': code, 'issues': issues})

data = resp2.json()
print(f"Response keys: {list(data.keys())}")
print(f"\n=== FULL RESPONSE ===")
print(json.dumps(data, indent=2))

print(f"\n=== SECURE CODE ONLY ===")
secure = data.get('secure_code', '')
print(f"[START]{secure}[END]")
print(f"\nLength: {len(secure)}")
print(f"Is same as original? {secure == code}")

#!/usr/bin/env python3
"""Debug what the backend is actually returning"""
import requests
import json

code = """import pickle
data = request.args.get('x')
obj = pickle.loads(data)"""

print("=" * 60)
print("Testing /analyze endpoint")
print("=" * 60)

# First analyze to get issues
resp1 = requests.post('http://localhost:8000/analyze', json={'code': code})
print(f"Status: {resp1.status_code}")
issues = resp1.json().get('issues', [])
print(f"Issues found: {len(issues)}")
print(json.dumps(issues, indent=2))

if issues:
    print("\n" + "=" * 60)
    print("Testing /analyze-with-ai endpoint")
    print("=" * 60)
    
    resp2 = requests.post('http://localhost:8000/analyze-with-ai', 
                         json={'code': code, 'issues': issues})
    print(f"Status: {resp2.status_code}")
    
    data = resp2.json()
    print(f"\nResponse keys: {list(data.keys())}")
    
    print(f"\n--- Analysis ---")
    print(data.get('analysis', ''))
    
    print(f"\n--- Secure Code ---")
    secure = data.get('secure_code', '')
    print(secure)
    print(f"Length: {len(secure)}")
    
    print(f"\n--- Explanation ---")
    print(data.get('explanation', ''))
    
    print("\n" + "=" * 60)
    print("Full response:")
    print("=" * 60)
    print(json.dumps(data, indent=2))

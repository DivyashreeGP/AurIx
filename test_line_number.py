#!/usr/bin/env python3
"""Test what the backend returns for line numbers"""
import requests
import json

code = """import pickle
data = request.args.get('x')
obj = pickle.loads(data)"""

print("Code has", len(code.split('\n')), "lines\n")

# Call backend
resp = requests.post('http://localhost:8000/analyze', json={'code': code})
issues = resp.json().get('issues', [])

print("Backend /analyze returns:")
for issue in issues:
    print(f"  Line: {issue.get('line')}")
    print(f"  Type: {issue.get('type')}")
    print(f"  Description: {issue.get('description', '')[:60]}")

# Now call AI endpoint
resp2 = requests.post('http://localhost:8000/analyze-with-ai', 
                     json={'code': code, 'issues': issues})

analysis_data = resp2.json()
print(f"\nBackend /analyze-with-ai analysis:")
print(analysis_data.get('analysis', '')[:200])

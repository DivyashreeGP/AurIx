#!/usr/bin/env python3
"""Debug: Check line numbers at each step"""
import requests
import json

code = """import pickle
data = request.args.get('x')
obj = pickle.loads(data)"""

print(f"Code has {len(code.splitlines())} lines\n")
print("=" * 60)

# Step 1: /analyze
print("Step 1: /analyze endpoint")
resp1 = requests.post('http://localhost:8000/analyze', json={'code': code})
issues = resp1.json().get('issues', [])
print(f"Issues returned: {len(issues)}")
for issue in issues:
    print(f"  Line: {issue.get('line')}")
    print(f"  Type: {issue.get('type')}")

print("\n" + "=" * 60)

# Step 2: /analyze-with-ai
print("Step 2: /analyze-with-ai endpoint")
resp2 = requests.post('http://localhost:8000/analyze-with-ai', 
                     json={'code': code, 'issues': issues})
result = resp2.json()
print(f"Analysis returned:\n{result.get('analysis', '')[:300]}")

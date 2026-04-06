#!/usr/bin/env python3
"""Direct test to show if secure code transformation is working"""
import requests
import sys

# Test case that definitely should transform
code_to_test = """import pickle
data = request.args.get('x')
obj = pickle.loads(data)"""

print("=" * 70)
print("DIRECT BACKEND TEST")
print("=" * 70)

# Step 1: Detect
print("\n[1] Calling /analyze endpoint...")
resp1 = requests.post('http://localhost:8000/analyze', json={'code': code_to_test})
issues = resp1.json().get('issues', [])
print(f"    Found {len(issues)} issues")

if not issues:
    print("    ERROR: No issues detected! Backend detection failed.")
    sys.exit(1)

# Step 2: Transform
print("\n[2] Calling /analyze-with-ai endpoint...")
resp2 = requests.post('http://localhost:8000/analyze-with-ai', 
                     json={'code': code_to_test, 'issues': issues})
data = resp2.json()

secure_code = data.get('secure_code', '')

print(f"\n[3] ANALYSIS RESULTS")
print("    " + "=" * 65)
print(f"    Original code:\n    {repr(code_to_test[:80])}")
print(f"\n    Secure code:\n    {repr(secure_code[:80])}")
print(f"\n    Are they the SAME? {code_to_test == secure_code}")
print(f"    Secure code length: {len(secure_code)}")

if code_to_test == secure_code:
    print("\n    [!] ISSUE: Backend is returning SAME code (no transformation)")
    print("        This means the template replacements are not being applied")
    sys.exit(1)
else:
    print("\n    [✓] SUCCESS: Backend IS transforming the code")
    print(f"        Original had 'pickle.loads': {'pickle.loads' in code_to_test}")
    print(f"        Secure has 'json.loads': {'json.loads' in secure_code}")
    sys.exit(0)

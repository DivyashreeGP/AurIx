#!/usr/bin/env python3
"""
Comprehensive test showing:
1. Backend detection
2. Code transformation
3. Whether Ollama/AI Engine is being used or templates
"""
import requests
import json

print("=" * 70)
print("DeVAIC: COMPLETE TRANSFORMATION TEST")
print("=" * 70)

# Test different vulnerability types
test_cases = [
    {
        "name": "Pickle Deserialization",
        "code": "import pickle\ndata = request.args.get('x')\nobj = pickle.loads(data)"
    },
    {
        "name": "SQL Injection",
        "code": "import sqlite3\nquery = f\"SELECT * FROM users WHERE id = '{user_id}'\"\ncursor.execute(query)"
    },
    {
        "name": "Eval Execution",
        "code": "result = eval(user_input)"
    },
    {
        "name": "Command Injection",
        "code": "import subprocess\nsubprocess.call(cmd, shell=True)"
    },
    {
        "name": "Hardcoded Credentials",
        "code": "password = \"admin123\"\napi_key = \"sk-1234567890abcdef\""
    },
    {
        "name": "MD5 Hash",
        "code": "import hashlib\nhash_val = hashlib.md5(data).hexdigest()"
    }
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n[Test {i}/{len(test_cases)}] {test_case['name']}")
    print("-" * 70)
    
    # Step 1: Detect vulnerabilities
    print("→ Detecting vulnerabilities...")
    resp1 = requests.post('http://localhost:8000/analyze', json={'code': test_case['code']})
    
    if resp1.status_code != 200:
        print(f"  ✗ Detection failed: {resp1.status_code}")
        continue
    
    issues = resp1.json().get('issues', [])
    if not issues:
        print(f"  ✓ No vulnerabilities detected (code is safe)")
        continue
    
    print(f"  ✓ Found {len(issues)} vulnerability(ies)")
    for issue in issues:
        print(f"    • {issue.get('type', 'Unknown')} (Line {issue.get('line', '?')})")
    
    # Step 2: Transform with AI/Template
    print("→ Transforming code to secure version...")
    resp2 = requests.post('http://localhost:8000/analyze-with-ai', 
                         json={'code': test_case['code'], 'issues': issues})
    
    if resp2.status_code != 200:
        print(f"  ✗ Transformation failed: {resp2.status_code}")
        continue
    
    data = resp2.json()
    secure_code = data.get('secure_code', '')
    
    if not secure_code or secure_code == test_case['code']:
        print(f"  ⚠ Secure code IS SAME as original (no transformation applied)")
        print(f"    This likely means Ollama is not running")
    else:
        print(f"  ✓ Code transformed to secure version")
        print(f"\n  ORIGINAL:\n    {test_case['code'][:80]}...")
        print(f"\n  SECURE:\n    {secure_code[:80]}...")
    
    # Show explanation summary
    explanation = data.get('explanation', '').split('\n')[0:3]
    if explanation:
        print(f"\n  Explanation (excerpt):")
        for line in explanation:
            if line.strip():
                print(f"    {line[:70]}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print("\nNOTE: If secure code matches original code, Ollama/Qwen 2.5 is not running.")
print("The backend is using template-based transformations instead.")
print("\nTo use AI-powered transformations:")
print("  1. Install Ollama from https://ollama.ai")
print("  2. Run: ollama run qwen2.5:7b")
print("  3. Restart backend and extension")

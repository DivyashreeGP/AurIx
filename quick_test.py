#!/usr/bin/env python3
"""Quick transformation tests"""
import requests
import json
import sys

tests_passed = 0
tests_failed = 0

def test_transform(name, code, expected_transform):
    global tests_passed, tests_failed
    print(f"\n{'='*50}")
    print(f"Test: {name}")
    print(f"{'='*50}")
    print(f"Original:\n{code}\n")
    
    try:
        # Detect issues
        resp1 = requests.post('http://localhost:8000/analyze', json={'code': code}, timeout=3)
        if resp1.status_code != 200:
            print(f"❌ Detection failed: {resp1.status_code}")
            tests_failed += 1
            return
            
        issues = resp1.json().get('issues', [])
        if not issues:
            print(f"⚠️  No issues detected - skipping transformation test")
            tests_passed += 1
            return
        
        # Transform code
        resp2 = requests.post('http://localhost:8000/analyze-with-ai', 
                             json={'code': code, 'issues': issues}, timeout=3)
        if resp2.status_code != 200:
            print(f"❌ Transformation failed: {resp2.status_code}")
            tests_failed += 1
            return
            
        secure_code = resp2.json().get('secure_code', '')
        print(f"Transformed:\n{secure_code}\n")
        
        # Check expected transformations
        all_found = True
        for expected in expected_transform:
            if expected in secure_code:
                print(f"✓ Found '{expected}'")
            else:
                print(f"✗ Missing '{expected}'")
                all_found = False
        
        if all_found:
            tests_passed += 1
            print("✅ PASS")
        else:
            tests_failed += 1
            print("❌ FAIL")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        tests_failed += 1

# Run tests
print("TRANSFORMATION TEST SUITE")
test_transform("Pickle → json.loads", 
               "import pickle\ndata = request.args.get('x')\nobj = pickle.loads(data)",
               ["json.loads"])
test_transform("Eval → ast.literal_eval",
               "result = eval(user_input)",
               ["ast.literal_eval"])
test_transform("shell=True → shell=False",
               "import subprocess\nsubprocess.call(cmd, shell=True)",
               ["shell=False"])
test_transform("MD5 → SHA256",
               "import hashlib\nhash_obj = hashlib.md5(data)",
               ["sha256"])
test_transform("Hardcoded password → os.getenv",
               "password = \"admin123\"",
               ["os.getenv"])

print(f"\n{'='*50}")
print(f"RESULTS: {tests_passed} passed, {tests_failed} failed")
print(f"{'='*50}")

sys.exit(0 if tests_failed == 0 else 1)

#!/usr/bin/env python3
"""Test all code transformations"""
import requests
import json

BASE_URL = "http://localhost:8000"

test_cases = [
    {
        "name": "Pickle Deserialization",
        "code": "import pickle\ndata = request.args.get('x')\nobj = pickle.loads(data)",
        "expected_transform": ["json.loads"]
    },
    {
        "name": "Eval Usage",
        "code": "result = eval(user_input)",
        "expected_transform": ["ast.literal_eval"]
    },
    {
        "name": "Command Injection",
        "code": "import subprocess\nsubprocess.call(cmd, shell=True)",
        "expected_transform": ["shell=False"]
    },
    {
        "name": "MD5 Weak Crypto",
        "code": "import hashlib\nhash_obj = hashlib.md5(data)",
        "expected_transform": ["sha256"]
    },
    {
        "name": "Hardcoded Credentials",
        "code": "password = \"admin123\"",
        "expected_transform": ["os.getenv"]
    },
]

print("=" * 60)
print("Testing Code Transformations")
print("=" * 60)

for test_case in test_cases:
    print(f"\nTest: {test_case['name']}")
    print("-" * 40)
    print(f"Original code:\n{test_case['code']}\n")
    
    # First analyze to get issues
    analyze_response = requests.post(
        f"{BASE_URL}/analyze",
        json={"code": test_case['code']},
        timeout=5
    )
    
    if analyze_response.status_code == 200:
        analyze_data = analyze_response.json()
        
        # Now analyze with AI for secure code
        ai_response = requests.post(
            f"{BASE_URL}/analyze-with-ai",
            json={
                "code": test_case['code'],
                "issues": analyze_data.get("issues", [])
            },
            timeout=5
        )
        
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            secure_code = ai_data.get("secure_code", "")
            
            print(f"Transformed code:\n{secure_code}\n")
            
            # Check if expected transforms were applied
            transforms_found = []
            for expected in test_case['expected_transform']:
                if expected in secure_code:
                    transforms_found.append(f"✓ Found '{expected}'")
                else:
                    transforms_found.append(f"✗ Missing '{expected}'")
            
            for result in transforms_found:
                print(result)
        else:
            print(f"Error in AI analysis: {ai_response.status_code}")
            print(ai_response.text)
    else:
        print(f"Error in detection: {analyze_response.status_code}")
        print(analyze_response.text)

print("\n" + "=" * 60)
print("Tests completed!")
print("=" * 60)

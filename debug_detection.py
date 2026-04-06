#!/usr/bin/env python3
"""Check if detection finds credentials"""
import requests
import json

test_code = 'api_key = "sk-1234567890abcdef"'

print("Testing detection of credentials...")
print(f"Code: {test_code}")

resp = requests.post('http://localhost:8000/analyze', json={'code': test_code})
if resp.status_code == 200:
    data = resp.json()
    issues = data.get('issues', [])
    print(f"Issues found: {len(issues)}")
    for issue in issues:
        print(f"  - {issue.get('type', 'Unknown')} (line {issue.get('line', '?')})")
    
    # Now try to transform
    print("\nNow testing transformation...")
    if issues:  # Only if we found issues
        ai_resp = requests.post('http://localhost:8000/analyze-with-ai', json={'code': test_code, 'issues': issues})
        if ai_resp.status_code == 200:
            ai_data = ai_resp.json()
            secure_code = ai_data.get('secure_code', '')
            print(f"Transformed: {secure_code}")
        else:
            print(f"Transform error: {ai_resp.status_code}")
    else:
        print("No issues detected, so no transformation attempted")
else:
    print(f"Detection error: {resp.status_code}")
    print(resp.text)

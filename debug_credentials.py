#!/usr/bin/env python3
"""Debug credentials transformation"""
import requests
import json

test_code = 'api_key = "sk-1234567890abcdef"'
issues = [{'type': 'Hardcoded Credentials', 'description': 'hardcoded API key', 'line': 1}]

print("Testing credentials transformation...")
print(f"Original code: {test_code}")

resp = requests.post('http://localhost:8000/analyze-with-ai', json={'code': test_code, 'issues': issues})
if resp.status_code == 200:
    data = resp.json()
    secure_code = data.get('secure_code', '')
    print(f"Transformed code: {secure_code}")
    print(f"Contains 'os.getenv': {'os.getenv' in secure_code}")
else:
    print(f"Error: {resp.status_code}")
    print(resp.text)

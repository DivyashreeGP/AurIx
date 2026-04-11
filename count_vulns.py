#!/usr/bin/env python3
"""Count vulnerabilities in ruleset files"""
import json
from pathlib import Path

ruleset_dir = Path('Rule_engine/ruleset')
total_vulns = 0
vuln_by_file = {}

for json_file in sorted(ruleset_dir.glob('*.json')):
    try:
        data = json.loads(json_file.read_text())
        if isinstance(data, list):
            count = len(data)
        else:
            count = len(data.get('rules', []))
        vuln_by_file[json_file.name] = count
        total_vulns += count
        print(f"{json_file.name:40} → {count:3} rules")
    except Exception as e:
        print(f"{json_file.name:40} → ERROR: {e}")

print("\n" + "="*60)
print(f"TOTAL VULNERABILITIES: {total_vulns}")
print("="*60)

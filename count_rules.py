import json
from pathlib import Path

rules = []
for f in Path('Rule-Engine/ruleset').glob('*.json'):
    rules.extend(json.load(open(f)))

print('=' * 60)
print('AURIX VULNERABILITY COVERAGE')
print('=' * 60)
print(f'Total Rules: {len(rules)}')
print(f'Rule Files: {len(list(Path("Rule-Engine/ruleset").glob("*.json")))}')
print()

# Group by category
cats = {}
for r in rules:
    vuln = r.get('vulnerabilities', 'UNKNOWN')
    cats[vuln] = cats.get(vuln, 0) + 1

print('VULNERABILITY CATEGORIES:')
print('-' * 40)
for k, v in sorted(cats.items(), key=lambda x: -x[1]):
    print(f'  {k:20} : {v:3} rules')
print()

# Severity mapping
print('SEVERITY BREAKDOWN:')
print('-' * 40)
high = sum(v for k, v in cats.items() if 'INJC' in k or 'IDAF' in k or 'SDIF' in k or 'CRYF' in k or 'BRAC' in k)
med = sum(v for k, v in cats.items() if 'SECM' in k or 'CRYP' in k)
low = sum(v for k, v in cats.items() if 'INSD' in k or 'SLMF' in k)
print(f'  HIGH:   {high}')
print(f'  MEDIUM: {med}')
print(f'  LOW:    {low}')
print()

# Rule files breakdown
print('RULE FILES:')
print('-' * 40)
for f in sorted(Path('Rule-Engine/ruleset').glob('*.json')):
    count = len(json.load(open(f)))
    print(f'  {f.stem:30} : {count:3} rules')
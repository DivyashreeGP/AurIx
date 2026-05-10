import json
from pathlib import Path

ruleset_dir = Path('Rule_Engine/ruleset')
rulesets = list(ruleset_dir.glob('*.json'))
print(f'Found {len(rulesets)} rulesets')

all_rules = []
for p in rulesets:
    try:
        rules = json.loads(p.read_text(encoding='utf-8', errors='ignore'))
        all_rules.extend(rules)
    except:
        pass

print(f'Total rules: {len(all_rules)}')
print('\nSample rules:')
for r in all_rules[:15]:
    print(f"  - {r.get('name', 'unnamed')}: {r.get('vulnerabilities', 'unknown')}")
    if 'pattern' in r:
        print(f"    Pattern: {r['pattern'][:60]}...")

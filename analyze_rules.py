import json
import os
import re

ruleset_dir = 'Rule_Engine/ruleset'

# Collect all rules and analyze patterns
print("=" * 70)
print("ANALYZING RULES FOR FALSE POSITIVE ISSUES")
print("=" * 70)

broad_patterns = []
total_rules = 0

for rule_file in sorted(os.listdir(ruleset_dir)):
    path = os.path.join(ruleset_dir, rule_file)
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            for rule in data.get('rules', []):
                total_rules += 1
                pattern = rule.get('pattern', '')
                
                # Check for overly broad patterns
                if pattern:
                    # Too generic patterns that might cause false positives
                    if pattern in [r'\b\w+\b', r'\w+', r'.*', r'.+', r'[\w\s]+']:
                        broad_patterns.append({
                            'file': rule_file,
                            'id': rule.get('id'),
                            'pattern': pattern,
                            'desc': rule.get('description', '')[:50]
                        })
                    
                    # Patterns that might be too generic
                    if len(pattern) < 5 and '|' not in pattern:
                        if pattern in broad_patterns:
                            continue
                        broad_patterns.append({
                            'file': rule_file,
                            'id': rule.get('id'),
                            'pattern': pattern,
                            'desc': rule.get('description', '')[:50]
                        })
    except Exception as e:
        pass

print(f"Total rules loaded: {total_rules}")
print(f"Potentially overly broad patterns: {len(broad_patterns)}\n")

# Show first 15 broad patterns
print("TOP BROAD PATTERNS (Potential False Positives):")
print("-" * 70)
for i, bp in enumerate(broad_patterns[:15], 1):
    print(f"{i}. File: {bp['file']}")
    print(f"   ID: {bp['id']}")
    print(f"   Pattern: {bp['pattern']}")
    print(f"   Description: {bp['desc']}\n")

# Now let's look at specific problematic patterns
print("\n" + "=" * 70)
print("ANALYZING SPECIFIC RULE CATEGORIES FOR FALSE POSITIVES")
print("=" * 70)

categories = {}
for rule_file in os.listdir(ruleset_dir):
    path = os.path.join(ruleset_dir, rule_file)
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            category = data.get('category', rule_file)
            if category not in categories:
                categories[category] = []
            
            for rule in data.get('rules', []):
                categories[category].append({
                    'id': rule.get('id'),
                    'pattern': rule.get('pattern', '')[:60],
                    'desc': rule.get('description', '')[:50]
                })
    except Exception as e:
        pass
        pass

for cat in list(categories.keys())[:5]:
    print(f"\n{cat}:")
    for rule in categories[cat][:3]:
        print(f"  - {rule['id']}: {rule['pattern']}")

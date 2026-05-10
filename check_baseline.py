import json

# Check baseline results
with open('results/report.json') as f:
    data = json.load(f)

print(f"Baseline Detection Results:")
print(f"Files scanned: {len(data.get('files', {}))}")

for filename, filedata in data.get('files', {}).items():
    vulns = filedata.get('vulnerabilities', [])
    print(f"\n{filename}: {len(vulns)} vulnerabilities")
    for v in vulns[:5]:
        print(f"  Line {v.get('line')}: {v.get('type')} - {v.get('message', '')[:60]}")

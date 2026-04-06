import os, json, re

RULESET_DIR = "version_2.0/ruleset"
bad = []

for fn in os.listdir(RULESET_DIR):
    if not fn.endswith(".json"): continue
    path = os.path.join(RULESET_DIR, fn)
    data = json.load(open(path, encoding="utf-8"))
    for rule in data:
        for key in ("pattern",):
            try:
                re.compile(rule[key])
            except re.error as e:
                bad.append((fn, rule.get("id"), key, rule[key], str(e)))
        for pn in rule.get("pattern_not", []):
            try:
                re.compile(pn)
            except re.error as e:
                bad.append((fn, rule.get("id"), "pattern_not", pn, str(e)))

if not bad:
    print("All rules compile ✅")
else:
    for fn, rid, k, pat, err in bad:
        print(f"[{fn}] {rid} -> {k} error: {err}\n  {pat}\n")

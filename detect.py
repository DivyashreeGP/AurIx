# detect.py  (semantic AST-based vulnerability scanner with compatibility wrappers)
import json, re, time, os, sys, argparse, ast
from pathlib import Path
from scanner.semantic import scan_file as semantic_scan_file
from scanner.taint import SemanticTaintAnalyzer, TaintVisitor

RULESET_DIR = Path("Rule-Engine/ruleset")
DEFAULT_EXCLUDES = {".git", ".venv", "venv", "__pycache__", "node_modules", "results"}

# ---------- REGEX FALLBACK ----------

def load_rules():
    rules = []
    if not RULESET_DIR.exists():
        return rules

    for p in RULESET_DIR.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for r in data:
            try:
                pattern = r.get("pattern", "")
                find_var = r.get("find_var", "")
                if find_var:
                    pattern = pattern.replace("VAR_PLACEHOLDER", find_var)
                elif "VAR_PLACEHOLDER" in pattern:
                    continue
                r["_pat"] = re.compile(pattern)
            except re.error:
                continue
            r["_pat_not"] = []
            for pn in r.get("pattern_not", []):
                try:
                    pn_processed = pn.replace("VAR_PLACEHOLDER", find_var) if find_var else pn
                    r["_pat_not"].append(re.compile(pn_processed))
                except re.error:
                    pass
            rules.append(r)
    return rules


def scan_line(line, rules):
    findings = []
    for r in rules:
        if r.get("_pat") and r["_pat"].search(line):
            if any(pn.search(line) for pn in r.get("_pat_not", [])):
                continue
            findings.append({
                "rule_id": r.get("id", ""),
                "vulnerabilities": [r.get("vulnerabilities", "")],
                "comment": "NULL"
            })
    return findings


def scan_file_regex(path, rules):
    results = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    for i, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue
        t0 = time.perf_counter()
        details = scan_line(line, rules)
        t1 = time.perf_counter()
        results.append({
            "snippet_number": i,
            "original_code": line,
            "vulnerable": bool(details),
            "vulnerabilities_summary": sorted({d["vulnerabilities"][0] for d in details}) if details else [],
            "comments": [],
            "execution_time": "{:.4f}".format(t1 - t0),
            "details": details
        })
    return results, lines


def taint_scan_file(path, lines):
    try:
        source = "".join(lines)
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []
    analyzer = SemanticTaintAnalyzer(lines)
    analyzer.visit(tree)
    out = []
    for finding in analyzer.findings:
        out.append({
            "snippet_number": finding["line"],
            "original_code": finding["code"],
            "vulnerable": True,
            "vulnerabilities_summary": [finding["title"]],
            "comments": [],
            "execution_time": "0.0000",
            "details": [{
                "rule_id": finding["rule_id"],
                "vulnerabilities": [finding["title"]],
                "confidence": finding["confidence"],
                "comment": finding["comment"],
            }]
        })
    return out


def merge_results(regex_results, taint_results):
    """Merge results from both engines while deduplicating findings."""
    seen = set()
    merged = []
    
    # Combine all results
    all_results = regex_results + taint_results
    
    for result in all_results:
        line = result.get("snippet_number")
        details = result.get("details", [])
        
        # Create a unique signature for this finding
        for detail in details:
            rule_id = detail.get("rule_id", "")
            vuln_type = detail.get("vulnerabilities", [""])[0]
            signature = (line, rule_id, vuln_type)
            
            if signature not in seen:
                seen.add(signature)
                merged.append(result)
                break
    
    # Sort by line number
    return sorted(merged, key=lambda x: x["snippet_number"])


def discover_targets(path):
    p = Path(path)
    if p.is_file() and p.suffix == ".py":
        return [p]
    files = []
    for dp, dns, fns in os.walk(p):
        dns[:] = [d for d in dns if d not in DEFAULT_EXCLUDES]
        for fn in fns:
            if fn.endswith(".py"):
                files.append(Path(dp) / fn)
    return files


def save_report(data, out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=4), encoding="utf-8")


def scan_file(path):
    return semantic_scan_file(Path(path))


def main():
    ap = argparse.ArgumentParser(description="AurIx Scanner (semantic AST + regex compatibility)")
    ap.add_argument("path", help="File or folder to scan")
    ap.add_argument("-o", "--out", default="results/report.json", help="Output JSON path")
    ap.add_argument("--only-issues", action="store_true", help="Omit non-vulnerable lines")
    ap.add_argument("--compact", action="store_true",
                    help="Emit a minimal report (line, rule_id, categories, code)")
    args = ap.parse_args()

    print("Loading rules...")
    rules = load_rules()

    targets = discover_targets(args.path)
    if not targets:
        print("No Python files found.")
        sys.exit(0)

    all_results = {}
    for t in targets:
        print(f"Scanning {t}...")
        semantic_results, _ = scan_file(t)
        merged = semantic_results

        if args.only_issues:
            merged = [e for e in merged if e.get("vulnerable")]

        if args.compact:
            compact = []
            for e in merged:
                cats = e.get("vulnerabilities_summary", [])
                dets = e.get("details", [])
                rids = [d.get("rule_id", "") for d in dets] or [""]
                compact.append({
                    "line": e["snippet_number"],
                    "rules": rids,
                    "categories": cats,
                    "code": e.get("original_code", "")
                })
            merged = compact

        all_results[str(t)] = merged

    print(f"\nSaving report to {args.out}...")
    save_report(all_results, args.out)
    print("Done.")


if __name__ == "__main__":
    main()

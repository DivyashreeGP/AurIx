# detect.py  (clean output: --only-issues, --compact)
import json, re, time, os, sys, argparse, ast
from pathlib import Path

RULESET_DIR = Path("Rule_engine/ruleset")
DEFAULT_EXCLUDES = {".git", ".venv", "venv", "__pycache__", "node_modules", "results"}

# ---------- TAINT (AST) ----------
TAINT_SOURCES = {
    ("request", "args", "get"),
    ("request", "form", "get"),
    ("request", "values", "get"),
    ("request", "args"),
    ("request", "form"),
    ("input",),
}
HTML_SINK_FUNCS = {("make_response",)}

class TaintVisitor(ast.NodeVisitor):
    def __init__(self, original_lines):
        self.tainted = set()
        self.findings = []
        self.lines = original_lines

    def _is_source(self, node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "input":
                return True
            if isinstance(node.func, ast.Attribute):
                chain = []
                f = node.func
                while isinstance(f, ast.Attribute):
                    chain.append(f.attr); f = f.value
                if isinstance(f, ast.Name):
                    chain.append(f.id); chain = tuple(reversed(chain))
                    return chain in TAINT_SOURCES
        if isinstance(node, ast.Subscript):
            base = node.value
            if (isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name)
                and base.value.id == "request" and base.attr in ("args","form","values")):
                return True
        return False

    def _expr_uses_tainted(self, node):
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and sub.id in self.tainted:
                return True
        return False

    def visit_Assign(self, node):
        if self._is_source(node.value) or self._expr_uses_tainted(node.value):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    self.tainted.add(t.id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if node.value and (self._is_source(node.value) or self._expr_uses_tainted(node.value)):
            if isinstance(node.target, ast.Name):
                self.tainted.add(node.target.id)
        self.generic_visit(node)

    def visit_Call(self, node):
        # app.run(debug=True)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "run":
            for kw in node.keywords or []:
                if kw.arg == "debug" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    ln = node.lineno
                    self.findings.append((ln, "DEBUG-TRUE-001", "Security Misconfiguration",
                                          self.lines[ln-1].strip()))
        # make_response(tainted)
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = (node.func.id,)
        elif isinstance(node.func, ast.Attribute):
            func_name = (node.func.attr,)
        if func_name in HTML_SINK_FUNCS:
            for arg in node.args:
                if self._is_source(arg) or self._expr_uses_tainted(arg):
                    ln = node.lineno
                    self.findings.append((ln, "REQUEST-ARGS_GET-005", "Broken Access Control",
                                          self.lines[ln-1].strip()))
        self.generic_visit(node)

    def visit_Return(self, node):
        if not node.value: return
        val = node.value
        tainted = self._is_source(val) or self._expr_uses_tainted(val)
        if isinstance(val, ast.JoinedStr):
            if any(isinstance(x, ast.FormattedValue) and self._expr_uses_tainted(x.value) for x in val.values):
                tainted = True
        if tainted:
            ln = node.lineno
            self.findings.append((ln, "REQUEST-ARGS_GET-006", "Broken Access Control",
                                  self.lines[ln-1].strip()))
        self.generic_visit(node)

def taint_scan_file(path, lines):
    try:
        tree = ast.parse("".join(lines), filename=str(path))
    except SyntaxError:
        return []
    v = TaintVisitor(lines); v.visit(tree)
    out = []
    for ln, rid, vuln, code in v.findings:
        out.append({
            "snippet_number": ln,
            "original_code": code,
            "vulnerable": True,
            "vulnerabilities_summary": [vuln],
            "comments": [],
            "execution_time": "0.0000",
            "details": [{"rule_id": rid, "vulnerabilities": [vuln], "comment": "NULL"}]
        })
    return out

# ---------- REGEX ----------
def load_rules():
    rules = []
    for p in RULESET_DIR.glob("*.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        for r in data:
            try:
                r["_pat"] = re.compile(r["pattern"])
            except re.error:
                continue
            r["_pat_not"] = []
            for pn in r.get("pattern_not", []):
                try:
                    r["_pat_not"].append(re.compile(pn))
                except re.error:
                    pass
            rules.append(r)
    return rules

def scan_line(line, rules):
    findings = []
    for r in rules:
        if r["_pat"].search(line):
            if any(pn.search(line) for pn in r["_pat_not"]):
                continue
            findings.append({
                "rule_id": r["id"],
                "vulnerabilities": [r["vulnerabilities"]],
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
            "vulnerabilities_summary": sorted({d["vulnerabilities"][0] for d in details}),
            "comments": [],
            "execution_time": f"{(t1 - t0):.4f}",
            "details": details
        })
    return results, lines

# ---------- MERGE ----------
def merge_results(regex_results, taint_results):
    def key(e):
        det = e.get("details", [])
        rid = det[0]["rule_id"] if det else ""
        return (e["snippet_number"], rid)
    merged = {key(e): e for e in regex_results}
    for e in taint_results:
        k = key(e)
        if k not in merged:
            merged[k] = e
        else:
            vs = set(merged[k].get("vulnerabilities_summary", []))
            for v in e.get("vulnerabilities_summary", []): vs.add(v)
            merged[k]["vulnerabilities_summary"] = sorted(vs)
            existing = {d["rule_id"] for d in merged[k].get("details", [])}
            for d in e.get("details", []):
                if d["rule_id"] not in existing:
                    merged[k]["details"].append(d)
    return [merged[k] for k in sorted(merged.keys(), key=lambda t: t[0])]

# ---------- DISCOVERY / SAVE ----------
def discover_targets(path):
    p = Path(path)
    if p.is_file() and p.suffix == ".py": return [p]
    files = []
    for dp, dns, fns in os.walk(p):
        dns[:] = [d for d in dns if d not in DEFAULT_EXCLUDES]
        for fn in fns:
            if fn.endswith(".py"): files.append(Path(dp)/fn)
    return files

def save_report(data, out_path):
    out_path = Path(out_path); out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=4), encoding="utf-8")

# ---------- MAIN ----------
def main():
    ap = argparse.ArgumentParser(description="AurIx Scanner (regex + AST taint)")
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
        print("No Python files found."); sys.exit(0)

    all_results = {}
    for t in targets:
        print(f"Scanning {t}...")
        regex_res, lines = scan_file_regex(t, rules)
        taint_res = taint_scan_file(t, lines)
        merged = merge_results(regex_res, taint_res)

        # apply --only-issues
        if args.only_issues:
            merged = [e for e in merged if e.get("vulnerable")]

        # apply --compact
        if args.compact:
            compact = []
            for e in merged:
                cats = e.get("vulnerabilities_summary", [])
                dets = e.get("details", [])
                rids = [d.get("rule_id","") for d in dets] or [""]
                compact.append({
                    "line": e["snippet_number"],
                    "rules": rids,
                    "categories": cats,
                    "code": e["original_code"]
                })
            merged = compact

        all_results[str(t)] = merged

    print(f"\nSaving report to {args.out}...")
    save_report(all_results, args.out)
    print("Done.")

if __name__ == "__main__":
    main()

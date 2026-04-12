# detect_improved.py (with false positive filtering)
import json, re, time, os, sys, argparse, ast
from pathlib import Path

RULESET_DIR = Path("Rule_Engine/ruleset")
DEFAULT_EXCLUDES = {".git", ".venv", "venv", "__pycache__", "node_modules", "results"}

# ========== FALSE POSITIVE FILTERS ==========
FP_FILTERS = {
    # XSS in backend-only contexts (not web-rendered)
    "XSS_BACKEND_SAFE": [
        r"print\(",           # Backend logging
        r"logger\.",          # Backend logger
        r"logging\.",         # Python logging module
        r"console\.log",      # Backend console
        r"sys\.stdout",       # Direct stdout
        r"sys\.stderr",       # Direct stderr
        r"return\s+{",        # JSON/dict returns
        r"json\.dumps",       # JSON serialization
    ],
    
    # HARDCODED_CREDENTIALS in safe contexts
    "HARDCODED_SAFE": [
        r"#\s*test|demo",     # Test/demo comments
        r"example|example\.com",  # Documentation/examples
        r"\'test\b|\"test\"|PASSWORD\s*=\s*\"test",  # Test data
        r"sha256|bcrypt|argon|hash",  # Crypto/hashing
        r"def\s+test_|def\s+demo",  # Test functions
        r"encryption_key\s*=\s*\"[A-Za-z0-9]{16,}\"",  # Proper key generation
    ],
    
    # UNVALIDATED_INPUT in safe contexts
    "UNVALIDATED_SAFE": [
        r"validated|sanitized|normalized",  # Already validated
        r"assert.*in\s+\[|isinstance\(.*\(int|str\)",  # Type checks
        r"regex\.|pattern\.|validation",  # Validation patterns
    ]
}

# MIN CONFIDENCE THRESHOLDS (increased from default)
CONFIDENCE_THRESHOLD = 0.70  # 70% confidence minimum

# ========== CONTEXT ANALYZER ==========
class ContextAnalyzer:
    def __init__(self, lines):
        self.lines = lines
        self.is_web_context = self._detect_web_context()
        self.is_test_file = self._detect_test_file()
    
    def _detect_web_context(self):
        """Detect if file is web-related (Flask/Django routes)"""
        content = "".join(self.lines[:50]).lower()  # First 50 lines
        return bool(re.search(r"@app\.(route|post|get|put|delete|patch)|@bp\.|flask|django|render", content))
    
    def _detect_test_file(self):
        """Detect if file is a test file"""
        content = "".join(self.lines[:20]).lower()
        return "test_" in content or "test" in content or "demo" in content
    
    def filter_xss(self, line, rule_id):
        """Filter XSS findings in non-web contexts"""
        if self.is_web_context:
            return True  # Keep in web context
        
        # Backend-only code: filter XSS
        for safe_pattern in FP_FILTERS["XSS_BACKEND_SAFE"]:
            if re.search(safe_pattern, line, re.IGNORECASE):
                return False
        return True
    
    def filter_credentials(self, line, rule_id):
        """Filter credential findings in safe contexts"""
        for safe_pattern in FP_FILTERS["HARDCODED_SAFE"]:
            if re.search(safe_pattern, line, re.IGNORECASE):
                return False
        return True
    
    def filter_validation(self, line, rule_id):
        """Filter unvalidated input findings where validation exists"""
        for safe_pattern in FP_FILTERS["UNVALIDATED_SAFE"]:
            if re.search(safe_pattern, line, re.IGNORECASE):
                return False
        return True
    
    def should_filter(self, vuln_type, line):
        """Main filter dispatcher"""
        if vuln_type == "XSS" or vuln_type == "XSS_VULNERABILITY":
            return not self.filter_xss(line, "")
        elif vuln_type == "HARDCODED_CREDENTIALS":
            return not self.filter_credentials(line, "")
        elif vuln_type in ["UNVALIDATED_INPUT", "INPUT_VALIDATION"]:
            return not self.filter_validation(line, "")
        return False

# ========== TAINT ANALYSIS (simplified) ==========
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

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "run":
            for kw in node.keywords or []:
                if kw.arg == "debug" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    ln = node.lineno
                    self.findings.append((ln, "DEBUG-TRUE-001", "Security Misconfiguration",
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
            "details": [{"rule_id": rid, "vulnerabilities": [vuln], "comment": "NULL"}],
            "confidence": 0.95  # Taint analysis has high confidence
        })
    return out

# ========== RULE-BASED DETECTION ==========
def load_rules():
    rules = []
    for p in RULESET_DIR.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except:
            continue
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

def scan_line(line, rules, confidence_threshold=CONFIDENCE_THRESHOLD):
    findings = []
    for r in rules:
        if r["_pat"].search(line):
            if any(pn.search(line) for pn in r["_pat_not"]):
                continue
            
            # Estimate confidence (simple: matches=high, close_to_exclude=lower)
            match_count = len(r["_pat"].findall(line))
            confidence = min(0.95, 0.50 + (match_count * 0.15))
            
            if confidence < confidence_threshold:
                continue  # Skip low-confidence matches
            
            findings.append({
                "rule_id": r["id"],
                "vulnerabilities": [r["vulnerabilities"]],
                "comment": "NULL",
                "confidence": confidence
            })
    return findings

def scan_file_regex(path, rules, context):
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
        
        # Apply context filters
        filtered_details = []
        for d in details:
            vuln_type = d["vulnerabilities"][0]
            if not context.should_filter(vuln_type, line):
                filtered_details.append(d)
        
        if filtered_details:  # Only add if not filtered
            results.append({
                "snippet_number": i,
                "original_code": line,
                "vulnerable": True,
                "vulnerabilities_summary": sorted({d["vulnerabilities"][0] for d in filtered_details}),
                "comments": [],
                "execution_time": f"{(t1 - t0):.4f}",
                "details": filtered_details,
                "confidence": sum(d.get("confidence", 0.75) for d in filtered_details) / len(filtered_details) if filtered_details else 0
            })
    
    return results, lines

# ========== MERGE ==========
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
    return [merged[k] for k in sorted(merged.keys(), key=lambda t: t[0])]

# ========== MAIN ==========
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

def main():
    ap = argparse.ArgumentParser(description="AurIx Scanner v2 (improved false positive filtering)")
    ap.add_argument("path", help="File or folder to scan")
    ap.add_argument("-o", "--out", default="results/report_improved.json", help="Output JSON path")
    ap.add_argument("--only-issues", action="store_true", help="Omit non-vulnerable lines")
    ap.add_argument("--compact", action="store_true", help="Emit a minimal report")
    args = ap.parse_args()

    print("Loading rules...")
    rules = load_rules()

    targets = discover_targets(args.path)
    if not targets:
        print("No Python files found."); sys.exit(0)

    all_results = {}
    for t in targets:
        print(f"Scanning {t}...")
        context = ContextAnalyzer([])  # Will be set per-file
        with open(t, "r", encoding="utf-8", errors="ignore") as f:
            file_lines = f.readlines()
        context = ContextAnalyzer(file_lines)
        
        regex_res, lines = scan_file_regex(t, rules, context)
        taint_res = taint_scan_file(t, lines)
        merged = merge_results(regex_res, taint_res)

        if args.only_issues:
            merged = [e for e in merged if e.get("vulnerable")]

        all_results[str(t)] = merged

    print(f"\nSaving report to {args.out}...")
    save_report(all_results, args.out)
    print("Done.")

if __name__ == "__main__":
    main()

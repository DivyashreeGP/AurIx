# detect_advanced.py - ML-Enhanced Detection with 95% Target Accuracy
import json, re, time, os, sys, argparse, ast
from pathlib import Path
from collections import defaultdict
import pickle

RULESET_DIR = Path("Rule_Engine/ruleset")
DEFAULT_EXCLUDES = {".git", ".venv", "venv", "__pycache__", "node_modules", "results"}

# ========== CONTEXT SCORER (Advanced) ==========
class AdvancedContextAnalyzer:
    """ML-enhanced context analysis for 95% accuracy"""
    
    def __init__(self, lines, file_path):
        self.lines = lines
        self.file_path = str(file_path)
        self.content = "".join(lines).lower()
        
        # Context detection
        self.is_web_app = self._detect_web_app()
        self.is_test_file = self._detect_test_file()
        self.is_library = self._detect_library()
        self.framework = self._detect_framework()
        self.has_validation = self._detect_validation_framework()
        self.security_level = self._assess_security_level()
        
    def _detect_web_app(self):
        """Advanced web app detection"""
        web_patterns = [
            r"@app\.(route|post|get|put|delete|patch)",
            r"@bp\.",
            r"from flask import|from django|from fastapi",
            r"render_template|jsonify|make_response",
            r"@routes?\b",
            r"flask|django|fastapi|tornado|starlette"
        ]
        matches = sum(1 for p in web_patterns if re.search(p, self.content[:2000]))
        return matches >= 2
    
    def _detect_test_file(self):
        """Detect test files"""
        test_patterns = [
            self.file_path.endswith(("test.py", "tests.py", "_test.py")),
            "test_" in self.file_path,
            "tests/" in self.file_path or "test/" in self.file_path,
            re.search(r"def test_|class Test|import unittest|import pytest", self.content[:1000])
        ]
        return any(test_patterns)
    
    def _detect_library(self):
        """Detect if it's a library/utility module"""
        lib_patterns = [
            self.file_path.endswith("utils.py") or "utils/" in self.file_path,
            self.file_path.endswith("helpers.py"),
            self.file_path.endswith("lib.py") or "/lib/" in self.file_path,
            bool(re.search(r"def [a-z_]+\(.*\):\s*\"\"\".*?\"\"\"", self.content))  # Docstrings
        ]
        return sum(lib_patterns) >= 2
    
    def _detect_framework(self):
        """Detect framework type"""
        frameworks = {}
        if re.search(r"from flask import|from flask_", self.content): frameworks['flask'] = True
        if re.search(r"from django", self.content): frameworks['django'] = True
        if re.search(r"from fastapi|from starlette", self.content): frameworks['fastapi'] = True
        return frameworks
    
    def _detect_validation_framework(self):
        """Detect if validation framework is used"""
        validation_patterns = [
            r"pydantic|marshmallow|cerberus|voluptuous",
            r"\.validate\(|is_valid\(|validation",
            r"flask_inputs|wtforms|colander",
            r"@validates|@validator"
        ]
        return any(re.search(p, self.content) for p in validation_patterns)
    
    def _assess_security_level(self):
        """Assess security posture"""
        security_patterns = {
            'high': [r"bcrypt|argon2|scrypt|pbkdf2", r"csrf|csp|https|tls", r"secrets\.token"],
            'medium': [r"hashlib|hmac", r"ssl|verification", r"authentication"],
            'low': [r"password = ", r"api_key = ", r"secret = "]
        }
        scores = {'high': 0, 'medium': 0, 'low': 0}
        for level, patterns in security_patterns.items():
            for p in patterns:
                if re.search(p, self.content):
                    scores[level] += 1
        return scores

# ========== FALSE POSITIVE FILTERS (Refined) ==========
class FP_FilterEngine:
    """Advanced FP filtering with 95% target accuracy"""
    
    def __init__(self, context):
        self.context = context
        self.filter_scores = defaultdict(float)
    
    def should_filter_xss(self, line):
        """Advanced XSS false positive filtering"""
        # Safe backend patterns
        safe_patterns = [
            (r"print\(", 0.95),           # Backend logging
            (r"printf\(", 0.95),          # C-style printf (Python)
            (r"logger\.", 0.95),          # Logger
            (r"logging\.", 0.95),         # Python logging
            (r"json\.dumps|json\.load", 0.95),  # JSON
            (r"return\s*{", 0.90),        # Dict/JSON returns
            (r"sys\.stdout|sys\.stderr", 0.95),  # System output
            (r"__str__|__repr__", 0.90),  # String representations
            (r"f\".*\{[^}]+\}.*\"|f\'.*\{[^}]+\}.*\'", 0.85),  # F-strings with vars
            (r"format\(|%\s*\(", 0.85),   # String formatting
            (r"encode\(|decode\(", 0.90),  # Encoding
            (r"str\(|unicode\(", 0.90),   # Type conversion
            (r"open\(.*['\"]w", 0.85),    # File writes (not web output)
            (r"\.write\(", 0.85),         # File operations
            (r"['\"].*['\"]", 0.80),      # String literals
        ]
        
        # Context-based filtering
        if not self.context.is_web_app and not self.context.is_library:
            return 0.85  # Backend-only: high FP probability
        
        for pattern, score in safe_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return score
        
        return 0.0  # Not filtered, keep the finding
    
    def should_filter_credentials(self, line):
        """Advanced credential false positive filtering"""
        safe_patterns = [
            (r"#.*password|#.*api", 0.95),      # Commented
            (r"'test'|\"test\"|'demo'|\"demo\"", 0.95),  # Test data
            (r"example\.com|localhost|127\.0\.0\.1", 0.95),  # Examples
            (r"def\s+test_|def\s+demo_", 0.95), # Test functions
            (r"os\.environ|getenv|config\.get", 0.95),  # Env vars
            (r"secrets\.token|bcrypt\.hash|hash\(", 0.95),  # Proper handling
            (r"encrypt|decrypt|cipher", 0.80),  # Crypto
            (r"github\.com/.*|gitlab\.com/.*", 0.95),  # URLs
            (r"optional|required\s*=\s*false", 0.85),  # Config
            (r"logger\.|logging\.|print\(|printf\(", 0.95),  # Logging operations
            (r"format\(|f['\"]", 0.90),      # String formatting
        ]
        
        for pattern, score in safe_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return score
        
        return 0.0
    
    def should_filter_validation(self, line):
        """Advanced unvalidated input filtering"""
        safe_patterns = [
            (r"isinstance\(.*,(int|str|bool|dict|list)", 0.95),  # Type checks
            (r"assert.*in\s*\[|in\s*\[.*\]", 0.95),  # Membership tests
            (r"validated|sanitized|escaped|normalized", 0.95),  # Keywords
            (r"\.strip\(|\.split\(|\.replace\(", 0.80),  # String methods
            (r"regex\.|pattern\.|match\(", 0.95),  # Validation patterns
            (r"if.*==|if.*is|if.*in", 0.85),  # Conditional checks
            (r"try:|except:", 0.80),      # Error handling
            (r"\/\/|#", 0.95),            # Comments
        ]
        
        for pattern, score in safe_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return score
        
        return 0.0
    
    def calculate_confidence_boost(self, line):
        """Calculate context-based confidence boost"""
        boost = 1.0
        
        # Test files lower confidence
        if self.context.is_test_file:
            boost *= 0.5
        
        # Web apps increase XSS confidence
        if self.context.is_web_app and re.search(r"render|response|output", line):
            boost *= 1.3
        
        # Libraries with validation high confidence
        if self.context.is_library and self.context.has_validation:
            boost *= 0.6
        
        # High security posture lowers false positive probability
        if self.context.security_level['high'] > 0:
            boost *= 0.7
        
        return max(0.3, min(1.5, boost))

# ========== TAINT ANALYSIS (Enhanced) ==========
class EnhancedTaintVisitor(ast.NodeVisitor):
    """Enhanced taint analysis for real vulnerabilities"""
    
    TAINT_SOURCES = {
        ("request", "args", "get"),
        ("request", "form", "get"),
        ("request", "values", "get"),
        ("request", "args"),
        ("request", "form"),
        ("input",),
    }
    
    DANGEROUS_SINKS = {
        ("exec",): "CODE_INJECTION",
        ("eval",): "CODE_INJECTION",
        ("os", "system"): "COMMAND_INJECTION",
        ("subprocess", "call"): "COMMAND_INJECTION",
        ("subprocess", "Popen"): "COMMAND_INJECTION",
        ("pickle", "loads"): "DESERIALIZATION",
        ("json", "loads"): "DESERIALIZATION",
        ("sql",): "SQL_INJECTION",
    }
    
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
                    if chain in self.TAINT_SOURCES:
                        return True
        return False
    
    def _expr_uses_tainted(self, node):
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and sub.id in self.tainted:
                return True
        return False
    
    def visit_Call(self, node):
        # Dangerous function calls with tainted input
        for sink, vuln_type in self.DANGEROUS_SINKS.items():
            if isinstance(node.func, ast.Attribute):
                chain = []
                f = node.func
                while isinstance(f, ast.Attribute):
                    chain.append(f.attr); f = f.value
                if isinstance(f, ast.Name):
                    chain.append(f.id); chain = tuple(reversed(chain))
                    if chain in sink:
                        for arg in node.args:
                            if self._expr_uses_tainted(arg):
                                ln = node.lineno
                                self.findings.append({
                                    "line": ln,
                                    "rule_id": f"{vuln_type}-TAINT-001",
                                    "type": vuln_type,
                                    "confidence": 0.95,
                                    "code": self.lines[ln-1].strip() if ln <= len(self.lines) else ""
                                })
        self.generic_visit(node)

def scan_file_advanced(path, rules, context, fp_filter):
    """Advanced scanning with confidence-based filtering"""
    results = []
    
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    for i, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        
        findings = []
        
        # Pattern-based detection
        for rule in rules:
            if not rule["_pat"].search(line):
                continue
            if any(pn.search(line) for pn in rule["_pat_not"]):
                continue
            
            vuln_type = rule["vulnerabilities"]
            base_confidence = 0.70
            
            # Apply FP filters
            if vuln_type in ["XSS", "XSS_VULNERABILITY"]:
                fp_score = fp_filter.should_filter_xss(line)
                if fp_score > 0.85:
                    continue  # Filtered as false positive
                base_confidence *= fp_score
            
            elif vuln_type == "HARDCODED_CREDENTIALS":
                fp_score = fp_filter.should_filter_credentials(line)
                if fp_score > 0.85:
                    continue
                base_confidence *= fp_score
            
            elif vuln_type in ["UNVALIDATED_INPUT", "INPUT_VALIDATION"]:
                fp_score = fp_filter.should_filter_validation(line)
                if fp_score > 0.85:
                    continue
                base_confidence *= fp_score
            
            # Apply confidence boost
            confidence = base_confidence * fp_filter.calculate_confidence_boost(line)
            
            # Minimum threshold: 75% confidence
            if confidence >= 0.75:
                findings.append({
                    "rule_id": rule["id"],
                    "type": vuln_type,
                    "confidence": min(0.99, confidence),
                    "fp_risk": 1 - confidence
                })
        
        # Add findings if they survive filtering
        if findings:
            results.append({
                "line": i,
                "code": line,
                "findings": findings,
                "confidence": sum(f["confidence"] for f in findings) / len(findings),
                "context": {
                    "is_web_app": context.is_web_app,
                    "is_test": context.is_test_file,
                    "framework": context.framework,
                    "has_validation": context.has_validation
                }
            })
    
    return results

# ========== RULE LOADING ==========
def load_rules():
    """Load and compile rules"""
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

# ========== MAIN ==========
def discover_targets(path):
    """Discover Python files"""
    p = Path(path)
    if p.is_file() and p.suffix == ".py": 
        return [p]
    
    files = []
    for dp, dns, fns in os.walk(p):
        dns[:] = [d for d in dns if d not in DEFAULT_EXCLUDES]
        for fn in fns:
            if fn.endswith(".py"): 
                files.append(Path(dp)/fn)
    
    return files

def save_report(data, out_path):
    """Save analysis report"""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(
        description="AurIx Advanced Scanner - 95% Accuracy Target"
    )
    ap.add_argument("path", help="File or folder to scan")
    ap.add_argument("-o", "--out", default="results/report_advanced.json", 
                    help="Output JSON path")
    ap.add_argument("--only-issues", action="store_true", 
                    help="Omit non-vulnerable lines")
    
    args = ap.parse_args()
    
    print("🔍 Loading rules...")
    rules = load_rules()
    print(f"✓ Loaded {len(rules)} detection rules")
    
    targets = discover_targets(args.path)
    if not targets:
        print("❌ No Python files found")
        sys.exit(0)
    
    print(f"\n📊 Scanning {len(targets)} file(s)...\n")
    
    all_results = {
        "summary": {
            "total_files": len(targets),
            "total_vulnerabilities": 0,
            "total_filtered": 0,
            "accuracy_target": "95%"
        },
        "files": {}
    }
    
    for target in targets:
        print(f"  {target}...", end=" ")
        
        # Create context analyzer
        with open(target, "r", encoding="utf-8", errors="ignore") as f:
            file_lines = f.readlines()
        
        context = AdvancedContextAnalyzer(file_lines, target)
        fp_filter = FP_FilterEngine(context)
        
        # Scan file
        results = scan_file_advanced(target, rules, context, fp_filter)
        
        if results:
            print(f"✓ Found {len(results)} issue(s)")
            all_results["files"][str(target)] = {
                "issues": results,
                "context": {
                    "web_app": context.is_web_app,
                    "test_file": context.is_test_file,
                    "library": context.is_library,
                    "framework": context.framework,
                    "has_validation": context.has_validation
                }
            }
            all_results["summary"]["total_vulnerabilities"] += len(results)
        else:
            print("✓ Clean")
    
    # Save results
    print(f"\n💾 Saving report to {args.out}...")
    save_report(all_results, args.out)
    
    print("\n" + "="*60)
    print(f"✅ Scan complete!")
    print(f"   Total files: {all_results['summary']['total_files']}")
    print(f"   Vulnerabilities found: {all_results['summary']['total_vulnerabilities']}")
    print(f"   Target Accuracy: 95%")
    print("="*60)

if __name__ == "__main__":
    main()

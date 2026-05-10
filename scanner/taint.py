import ast
from typing import List, Tuple
from .ast_utils import get_call_chain, is_string_literal, any_name_in_expr
from .report import build_finding


class SemanticTaintAnalyzer(ast.NodeVisitor):
    TAINT_SOURCES = {
        ("request", "args", "get"),
        ("request", "form", "get"),
        ("request", "values", "get"),
        ("request", "args"),
        ("request", "form"),
        ("input",),
    }

    SANITIZER_CALLS = {
        ("escape",),
        ("html", "escape"),
        ("re", "escape"),
        ("urllib", "parse", "quote"),
        ("urllib", "parse", "quote_plus"),
        ("hmac", "new"),
        ("hashlib", "sha256"),
        ("hashlib", "pbkdf2_hmac"),
        ("bcrypt", "hashpw"),
    }

    DANGEROUS_SINKS = {
        ("eval",): {
            "rule_id": "CODE_INJECTION-001",
            "title": "Code Injection",
            "confidence": 0.96,
            "comment": "User-controlled data passed to eval() is dangerous.",
        },
        ("exec",): {
            "rule_id": "CODE_INJECTION-002",
            "title": "Code Injection",
            "confidence": 0.96,
            "comment": "User-controlled data passed to exec() is dangerous.",
        },
        ("os", "system"): {
            "rule_id": "COMMAND_INJECTION-001",
            "title": "Command Injection",
            "confidence": 0.93,
            "comment": "User-controlled data passed to os.system() may execute shell commands.",
        },
        ("subprocess", "Popen"): {
            "rule_id": "COMMAND_INJECTION-002",
            "title": "Command Injection",
            "confidence": 0.93,
            "comment": "Subprocess spawning with untrusted data can lead to command injection.",
        },
        ("subprocess", "call"): {
            "rule_id": "COMMAND_INJECTION-003",
            "title": "Command Injection",
            "confidence": 0.93,
            "comment": "Subprocess call with untrusted data may execute shell commands.",
        },
        ("subprocess", "run"): {
            "rule_id": "COMMAND_INJECTION-004",
            "title": "Command Injection",
            "confidence": 0.93,
            "comment": "Subprocess run with untrusted data may execute shell commands.",
        },
        ("pickle", "loads"): {
            "rule_id": "DESERIALIZATION-001",
            "title": "Insecure Deserialization",
            "confidence": 0.90,
            "comment": "pickle.loads() on untrusted input is unsafe.",
        },
        ("pickle", "load"): {
            "rule_id": "DESERIALIZATION-002",
            "title": "Insecure Deserialization",
            "confidence": 0.90,
            "comment": "pickle.load() on untrusted input is unsafe.",
        },
        ("yaml", "load"): {
            "rule_id": "DESERIALIZATION-003",
            "title": "Insecure Deserialization",
            "confidence": 0.90,
            "comment": "yaml.load() on untrusted input can execute arbitrary code.",
        },
    }

    SQL_SINK_NAMES = {"execute", "executemany", "callproc"}
    XSS_SINK_NAMES = {"make_response", "render_template", "render"}
    SAFE_WEB_SINKS = {"jsonify", "Response", "make_response"}
    HARD_CODED_NAMES = {
        "password",
        "passwd",
        "secret",
        "api_key",
        "token",
        "access_token",
        "aws_secret",
        "db_password",
    }

    def __init__(self, lines: List[str]):
        self.lines = lines
        self.tainted = set()
        self.findings = []

    def _is_source(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Call):
            chain = get_call_chain(node)
            return chain in self.TAINT_SOURCES

        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute):
            chain = get_call_chain(node.value)
            return chain in self.TAINT_SOURCES

        return False

    def _is_sanitized(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Call):
            chain = get_call_chain(node)
            if chain in self.SANITIZER_CALLS:
                return any(self._expr_is_tainted(arg) for arg in node.args)

        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and get_call_chain(sub) in self.SANITIZER_CALLS:
                return True

        return False

    def _expr_is_tainted(self, node: ast.AST) -> bool:
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and sub.id in self.tainted:
                return True
        return False

    def _assign_name(self, target: ast.AST) -> None:
        if isinstance(target, ast.Name):
            self.tainted.add(target.id)
        elif isinstance(target, ast.Tuple):
            for elt in target.elts:
                self._assign_name(elt)

    def _is_hardcoded_credential(self, target: ast.AST, value: ast.AST) -> bool:
        if not is_string_literal(value):
            return False

        if isinstance(target, ast.Name) and target.id.lower() in self.HARD_CODED_NAMES:
            return True

        if isinstance(target, ast.Attribute) and target.attr.lower() in self.HARD_CODED_NAMES:
            return True

        return False

    def _safe_subprocess(self, node: ast.Call) -> bool:
        if any(
            kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is False
            for kw in node.keywords
        ):
            return True

        if node.args and isinstance(node.args[0], (ast.List, ast.Tuple)):
            return True

        return False

    def _has_tainted_arg(self, node: ast.Call) -> bool:
        for arg in node.args:
            if self._expr_is_tainted(arg) and not self._is_sanitized(arg):
                return True
        for kw in node.keywords:
            if self._expr_is_tainted(kw.value) and not self._is_sanitized(kw.value):
                return True
        return False

    def _add_finding(self, line: int, rule_id: str, title: str, confidence: float, comment: str) -> None:
        self.findings.append({
            "line": line,
            "rule_id": rule_id,
            "title": title,
            "confidence": confidence,
            "comment": comment,
            "code": self.lines[line - 1].strip() if 1 <= line <= len(self.lines) else "",
        })

    def visit_Assign(self, node: ast.Assign) -> None:
        if self._is_source(node.value) or self._expr_is_tainted(node.value):
            if not self._is_sanitized(node.value):
                for target in node.targets:
                    self._assign_name(target)

        for target in node.targets:
            if self._is_hardcoded_credential(target, node.value):
                line = node.lineno
                self._add_finding(
                    line,
                    "HARDCODED_CREDENTIALS-001",
                    "Hard-coded Credentials",
                    0.88,
                    "Hard-coded secret assigned directly in source code.",
                )

        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value and (self._is_source(node.value) or self._expr_is_tainted(node.value)):
            if not self._is_sanitized(node.value) and isinstance(node.target, ast.Name):
                self._assign_name(node.target)

        if node.value and self._is_hardcoded_credential(node.target, node.value):
            line = node.lineno
            self._add_finding(
                line,
                "HARDCODED_CREDENTIALS-001",
                "Hard-coded Credentials",
                0.88,
                "Hard-coded secret assigned directly in source code.",
            )

        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if self._expr_is_tainted(node.value):
            self._assign_name(node.target)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        chain = get_call_chain(node)

        if isinstance(node.func, ast.Attribute) and node.func.attr == "run":
            for kw in node.keywords or []:
                if kw.arg == "debug" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self._add_finding(
                        node.lineno,
                        "DEBUG-TRUE-001",
                        "Security Misconfiguration",
                        0.75,
                        "Debug mode is enabled in production-like code.",
                    )

        # Dangerous sinks even without taint (for static analysis)
        dangerous_sinks = {
            ("eval",): {
                "rule_id": "CODE_INJECTION-001",
                "title": "Code Injection",
                "confidence": 0.95,
                "comment": "eval() is inherently dangerous and should be avoided.",
            },
            ("exec",): {
                "rule_id": "CODE_INJECTION-002",
                "title": "Code Injection",
                "confidence": 0.95,
                "comment": "exec() is inherently dangerous and should be avoided.",
            },
            ("os", "system"): {
                "rule_id": "COMMAND_INJECTION-001",
                "title": "Command Injection",
                "confidence": 0.90,
                "comment": "os.system() can lead to command injection.",
            },
            ("pickle", "loads"): {
                "rule_id": "DESERIALIZATION-001",
                "title": "Insecure Deserialization",
                "confidence": 0.95,
                "comment": "pickle.loads() is unsafe for untrusted data.",
            },
            ("pickle", "load"): {
                "rule_id": "DESERIALIZATION-002",
                "title": "Insecure Deserialization",
                "confidence": 0.95,
                "comment": "pickle.load() is unsafe for untrusted data.",
            },
            ("yaml", "load"): {
                "rule_id": "DESERIALIZATION-003",
                "title": "Insecure Deserialization",
                "confidence": 0.95,
                "comment": "yaml.load() can execute arbitrary code.",
            },
        }

        if chain in dangerous_sinks:
            self._add_finding(
                node.lineno,
                dangerous_sinks[chain]["rule_id"],
                dangerous_sinks[chain]["title"],
                dangerous_sinks[chain]["confidence"],
                dangerous_sinks[chain]["comment"],
            )

        if chain in self.DANGEROUS_SINKS and self._has_tainted_arg(node):
            if chain == ("subprocess", "run") and self._safe_subprocess(node):
                return
            self._add_finding(
                node.lineno,
                self.DANGEROUS_SINKS[chain]["rule_id"],
                self.DANGEROUS_SINKS[chain]["title"],
                self.DANGEROUS_SINKS[chain]["confidence"],
                self.DANGEROUS_SINKS[chain]["comment"],
            )

        if chain and chain[-1] in self.SQL_SINK_NAMES:
            # Check for string concatenation in SQL
            if self._is_sql_injection_risk(node):
                self._add_finding(
                    node.lineno,
                    "SQL_INJECTION-001",
                    "SQL Injection",
                    0.92,
                    "Possible SQL injection due to string-based query construction.",
                )
            elif self._has_tainted_arg(node):
                self._add_finding(
                    node.lineno,
                    "SQL_INJECTION-001",
                    "SQL Injection",
                    0.92,
                    "Parameterized queries are recommended when using SQL execution functions.",
                )

        if chain and chain[-1] in self.XSS_SINK_NAMES and self._has_tainted_arg(node):
            self._add_finding(
                node.lineno,
                "XSS-001",
                "Cross-Site Scripting",
                0.85,
                "User-controlled data returned in an HTML response may lead to XSS.",
            )

        if chain and chain[-1] == "jsonify":
            # JSON serialization is safe for values that are not directly rendered as HTML
            if self._has_tainted_arg(node):
                self._add_finding(
                    node.lineno,
                    "JSON_SAFE-001",
                    "Suspicious Use",
                    0.40,
                    "jsonify() is generally safe, but review how user input is handled.",
                )

        self.generic_visit(node)

    def _is_sql_injection_risk(self, node: ast.Call) -> bool:
        """Check if SQL call has string concatenation indicating injection risk."""
        for arg in node.args:
            if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                # Check if one side is a string literal and other is variable
                left_str = isinstance(arg.left, ast.Constant) and isinstance(arg.left.value, str)
                right_var = isinstance(arg.right, ast.Name)
                if left_str and right_var:
                    return True
                left_var = isinstance(arg.left, ast.Name)
                right_str = isinstance(arg.right, ast.Constant) and isinstance(arg.right.value, str)
                if left_var and right_str:
                    return True
        return False

    def visit_Return(self, node: ast.Return) -> None:
        if node.value and self._expr_is_tainted(node.value) and not self._is_sanitized(node.value):
            self._add_finding(
                node.lineno,
                "BROKEN_ACCESS_CONTROL-001",
                "Broken Access Control",
                0.80,
                "Returning user-controlled data can expose sensitive information.",
            )
        self.generic_visit(node)


class LegacyTaintVisitor(SemanticTaintAnalyzer):
    """Legacy compatibility wrapper for tuple-based findings consumers."""

    def __init__(self, lines: List[str]):
        super().__init__(lines)
        self.findings = []

    def _add_finding(self, line: int, rule_id: str, title: str, confidence: float, comment: str) -> None:
        self.findings.append((line, rule_id, title, self.lines[line - 1].strip() if 1 <= line <= len(self.lines) else ""))


TaintVisitor = LegacyTaintVisitor

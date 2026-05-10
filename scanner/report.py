from typing import Dict

SEVERITY_MAP = {
    "Code Injection": "high",
    "Command Injection": "high",
    "SQL Injection": "high",
    "Insecure Deserialization": "high",
    "Broken Access Control": "high",
    "Cross-Site Scripting": "medium",
    "Hard-coded Credentials": "medium",
    "Weak Cryptography": "medium",
    "Security Misconfiguration": "medium",
    "Suspicious Use": "low",
}

CWE_MAP = {
    "Code Injection": "CWE-94",
    "Command Injection": "CWE-77",
    "SQL Injection": "CWE-89",
    "Insecure Deserialization": "CWE-502",
    "Broken Access Control": "CWE-284",
    "Cross-Site Scripting": "CWE-79",
    "Hard-coded Credentials": "CWE-798",
    "Weak Cryptography": "CWE-326",
    "Security Misconfiguration": "CWE-933",
    "Suspicious Use": "CWE-693",
}

VULN_TYPE_MAP = {
    "Code Injection": "Code Injection",
    "Command Injection": "Command Injection",
    "SQL Injection": "SQL Injection",
    "Insecure Deserialization": "Insecure Deserialization",
    "Broken Access Control": "Broken Access Control",
    "Cross-Site Scripting": "Cross-Site Scripting",
    "Hard-coded Credentials": "Hard-coded Credentials",
    "Weak Cryptography": "Weak Cryptography",
    "Security Misconfiguration": "Security Misconfiguration",
    "Suspicious Use": "Suspicious Use",
}


def build_finding(line: int, code: str, rule_id: str, title: str, confidence: float, comment: str = "") -> Dict:
    return {
        "snippet_number": line,
        "original_code": code,
        "vulnerable": True,
        "vulnerabilities_summary": [title],
        "comments": [],
        "execution_time": "0.0000",
        "details": [{
            "rule_id": rule_id,
            "vulnerabilities": [title],
            "cwe": CWE_MAP.get(title, "CWE-000"),
            "confidence": confidence,
            "comment": comment or "Detected by semantic AST analysis"
        }],
        "confidence": confidence,
        "category": title,
    }

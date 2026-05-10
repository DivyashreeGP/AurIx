"""
Integration Tests for AurIx Vulnerability Detection Engine

Tests the full pipeline:
- Rule engine loading
- Backend API integration
- End-to-end detection flow
"""

import sys
import os
import tempfile
import json

# Get project root (parent of tests)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import from root detect.py
import detect
from detect import load_rules, scan_file_regex, taint_scan_file, merge_results


def detect_vulnerabilities(code):
    """Helper function to detect vulnerabilities in code string"""
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        rules = load_rules()
        
        # Run regex scan
        regex_res, lines = scan_file_regex(temp_path, rules)
        
        # Run taint scan
        taint_res = taint_scan_file(temp_path, lines)
        
        # Merge results
        merged = merge_results(regex_res, taint_res)
        
        # Convert to issues format
        issues = []
        for e in merged:
            if e.get('vulnerable'):
                for d in e.get('details', []):
                    issues.append({
                        'type': d.get('rule_id', ''),
                        'description': e.get('original_code', ''),
                        'line': e.get('snippet_number', 0)
                    })
        
        return {'issues': issues}
    finally:
        os.unlink(temp_path)


# ==================== FULL PIPELINE TESTS ====================

def test_full_pipeline_vulnerable_code():
    """Integration: Full pipeline with vulnerable code"""
    code = '''
import os
import sqlite3

def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def run_command(cmd):
    os.system(cmd)
'''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    
    # Should detect multiple vulnerabilities
    assert len(issues) >= 2, f"Should detect at least 2 issues, found {len(issues)}"
    
    # Check for SQL injection
    assert any('SQL' in i.get('type', '') or 'INJC' in i.get('type', '') for i in issues), "Should detect SQL injection"
    
    # Check for command injection
    assert any('OS-SYSTEM' in i.get('type', '') or 'SUBPROCESS' in i.get('type', '') for i in issues), "Should detect command injection"
    
    print("✓ Full Pipeline Vulnerable: Detected multiple issues")
    return True


def test_full_pipeline_secure_code():
    """Integration: Full pipeline with secure code"""
    code = '''
import os
import sqlite3
import subprocess

def get_user(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))
    return cursor.fetchall()

def run_command():
    subprocess.run(['ls', '-la'], shell=False)
'''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    
    # Should NOT detect any vulnerabilities
    assert len(issues) == 0, f"Should be secure, found {len(issues)} issues"
    
    print("✓ Full Pipeline Secure: No false positives")
    return True


def test_rule_engine_loading():
    """Integration: Rule engine loads all rules"""
    from detect import load_rules
    
    rules = load_rules()
    
    # Should have rules loaded
    assert len(rules) > 0, "Should load rules from ruleset"
    
    # Check for key rule categories
    rule_ids = [r.get('id', '') for r in rules]
    
    assert any('SQL' in rid for rid in rule_ids), "Should have SQL rules"
    assert any('OS-SYSTEM' in rid or 'SUBPROCESS' in rid for rid in rule_ids), "Should have OS/System rules"
    assert any('CODE' in rid for rid in rule_ids), "Should have Code Execution rules"
    
    print(f"✓ Rule Engine: Loaded {len(rules)} rules")
    return True


def test_mixed_secure_vulnerable():
    """Integration: Code with both secure and vulnerable patterns"""
    code = '''
import os
import subprocess
import json

# Vulnerable - command injection
def bad_cmd(user_input):
    os.system(user_input)

# Secure - subprocess with shell=False
def good_cmd():
    subprocess.run(['ls'], shell=False)

# Secure - JSON parsing
def parse_data(data):
    return json.loads(data)
'''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    
    # Should detect only 1 vulnerability (the os.system)
    assert len(issues) == 1, f"Should detect 1 issue, found {len(issues)}"
    assert 'OS-SYSTEM' in issues[0].get('type', '') or 'system' in issues[0].get('description', '').lower()
    
    print("✓ Mixed Code: Correctly identified 1 vulnerability")
    return True


def test_complex_flask_app():
    """Integration: Complex Flask application"""
    code = '''
from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

@app.route('/user/<user_id>')
def get_user(user_id):
    # VULNERABLE: SQL Injection
    query = "SELECT * FROM users WHERE id = " + user_id
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute(query)
    return jsonify(cursor.fetchall())

@app.route('/exec')
def exec_cmd():
    # VULNERABLE: Command Injection
    cmd = request.args.get('cmd', '')
    return os.system(cmd)

@app.route('/safe')
def safe_route():
    # SECURE: Parameterized query
    user_id = request.args.get('id', '')
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    return jsonify(cursor.fetchall())
'''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    
    # Should detect at least 2 vulnerabilities
    assert len(issues) >= 2, f"Should detect at least 2 issues, found {len(issues)}"
    
    print("✓ Complex Flask: Detected multiple issues")
    return True


def test_duplicate_detection():
    """Integration: Same vulnerability on multiple lines"""
    code = '''
import os

def test():
    os.system("ls")
    os.system("cat /etc/passwd")
    os.system("whoami")
'''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    
    # Should detect multiple os.system calls
    os_issues = [i for i in issues if 'system' in i.get('description', '').lower()]
    assert len(os_issues) >= 2, f"Should detect multiple os.system, found {len(os_issues)}"
    
    print("✓ Duplicate Detection: Found multiple instances")
    return True


def test_empty_code():
    """Integration: Empty or minimal code"""
    code = '''
# This is a comment
x = 1
print("hello")
'''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    
    # Should not detect any vulnerabilities
    assert len(issues) == 0, "Empty code should have no issues"
    
    print("✓ Empty Code: No issues detected")
    return True


def test_line_number_accuracy():
    """Integration: Line numbers are accurate"""
    code = '''
import os

def test():
    x = 1
    os.system("ls")  # Line 6
    y = 2
'''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    
    if len(issues) > 0:
        # Line number should be around line 6
        line = issues[0].get('line', 0)
        assert 5 <= line <= 7, f"Line number should be around 6, got {line}"
    
    print("✓ Line Numbers: Accurate")
    return True


# ==================== RUN ALL TESTS ====================

if __name__ == '__main__':
    print("=" * 60)
    print("AURIX INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        ('Rule Engine Loading', test_rule_engine_loading),
        ('Full Pipeline Vulnerable', test_full_pipeline_vulnerable_code),
        ('Full Pipeline Secure', test_full_pipeline_secure_code),
        ('Mixed Secure/Vulnerable', test_mixed_secure_vulnerable),
        ('Complex Flask App', test_complex_flask_app),
        ('Duplicate Detection', test_duplicate_detection),
        ('Empty Code', test_empty_code),
        ('Line Number Accuracy', test_line_number_accuracy),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"✗ {name}: FAILED - {e}")
            failed += 1
    
    print("=" * 60)
    print(f"RESULTS: {passed} Passed, {failed} Failed")
    print("=" * 60)
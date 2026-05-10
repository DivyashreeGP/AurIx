"""
Unit Tests for AurIx Vulnerability Detection Engine

Tests each rule category with:
- Positive test (vulnerable code should be detected)
- Negative test (secure code should NOT be detected)
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


# ==================== SQL INJECTION TESTS ====================

def test_sql_001_positive():
    """SQL-001: SQL Injection via string concatenation"""
    code = '''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert any('SQL' in i.get('type', '') for i in issues), "Should detect SQL injection"
    print("✓ SQL-001 Positive: Detected")

def test_sql_001_negative():
    """SQL-001: Secure parameterized query"""
    code = '''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert len(issues) == 0, "Should NOT detect vulnerability (secure code)"
    print("✓ SQL-001 Negative: Passed (no false positive)")


# ==================== COMMAND INJECTION TESTS ====================

def test_os_system_positive():
    """OS-SYSTEM-002: os.system with user input"""
    code = '''
import os
def run_cmd(cmd):
    os.system(cmd)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert any('OS-SYSTEM' in i.get('type', '') for i in issues), "Should detect os.system"
    print("✓ OS-SYSTEM Positive: Detected")

def test_os_system_negative():
    """OS-SYSTEM: Secure subprocess with shell=False"""
    code = '''
import subprocess
def run_cmd():
    subprocess.run(['ls', '-la'], shell=False)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert len(issues) == 0, "Should NOT detect (secure)"
    print("✓ OS-SYSTEM Negative: Passed")


# ==================== PATH TRAVERSAL TESTS ====================

def test_path_traversal_positive():
    """PATH-001: Path traversal via user input"""
    code = '''
import os
def read_file(filename):
    return open('/var/www/' + filename).read()
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert any('PATH' in i.get('type', '') for i in issues), "Should detect path traversal"
    print("✓ PATH-001 Positive: Detected")

def test_path_traversal_negative():
    """PATH: Secure path with validation"""
    code = '''
import os
def read_file(filename):
    if not filename.startswith('/'):
        filename = '/safe/' + filename
    return open(filename).read()
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert len(issues) == 0, "Should NOT detect (validated)"
    print("✓ PATH-001 Negative: Passed")


# ==================== CODE EXECUTION TESTS ====================

def test_eval_positive():
    """CODE-001: eval with user input"""
    code = '''
def execute_code(user_input):
    eval(user_input)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert any('CODE' in i.get('type', '') or 'eval' in i.get('description', '').lower() for i in issues), "Should detect eval"
    print("✓ CODE-001 Positive: Detected")

def test_eval_negative():
    """CODE: Secure with ast.literal_eval"""
    code = '''
import ast
def safe_parse(user_input):
    return ast.literal_eval(user_input)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert len(issues) == 0, "Should NOT detect (safe parser)"
    print("✓ CODE-001 Negative: Passed")


# ==================== DESERIALIZATION TESTS ====================

def test_pickle_positive():
    """DESER-001: insecure pickle.loads"""
    code = '''
import pickle
def load_data(data):
    return pickle.loads(data)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert any('DESER' in i.get('type', '') for i in issues), "Should detect pickle"
    print("✓ DESER-001 Positive: Detected")

def test_pickle_negative():
    """DESER: Secure with json.loads"""
    code = '''
import json
def load_data(data):
    return json.loads(data)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert len(issues) == 0, "Should NOT detect (JSON)"
    print("✓ DESER-001 Negative: Passed")


# ==================== YAML TESTS ====================

def test_yaml_positive():
    """YAML-001: insecure yaml.load"""
    code = '''
import yaml
def load_config(data):
    return yaml.load(data)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert any('YAML' in i.get('type', '') for i in issues), "Should detect yaml.load"
    print("✓ YAML-001 Positive: Detected")

def test_yaml_negative():
    """YAML: Secure with yaml.safe_load"""
    code = '''
import yaml
def load_config(data):
    return yaml.safe_load(data)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert len(issues) == 0, "Should NOT detect (safe_load)"
    print("✓ YAML-001 Negative: Passed")


# ==================== SUBPROCESS TESTS ====================

def test_subprocess_positive():
    """SUBPROCESS-001: subprocess with shell=True"""
    code = '''
import subprocess
def run_cmd(cmd):
    subprocess.run(cmd, shell=True)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert any('SUBPROCESS' in i.get('type', '') or 'shell=True' in i.get('description', '') for i in issues), "Should detect shell=True"
    print("✓ SUBPROCESS-001 Positive: Detected")

def test_subprocess_negative():
    """SUBPROCESS: Secure with shell=False"""
    code = '''
import subprocess
def run_cmd():
    subprocess.run(['ls', '-la'], shell=False)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert len(issues) == 0, "Should NOT detect (shell=False)"
    print("✓ SUBPROCESS-001 Negative: Passed")


# ==================== HARDCODED SECRETS TESTS ====================

def test_hardcoded_secret_positive():
    """SECRET-001: Hardcoded API key"""
    code = '''
API_KEY = "sk-1234567890abcdef"
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert any('SECRET' in i.get('type', '') or 'API_KEY' in i.get('description', '') for i in issues), "Should detect hardcoded secret"
    print("✓ SECRET-001 Positive: Detected")

def test_hardcoded_secret_negative():
    """SECRET: Using environment variable"""
    code = '''
import os
API_KEY = os.environ.get('API_KEY')
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert len(issues) == 0, "Should NOT detect (env var)"
    print("✓ SECRET-001 Negative: Passed")


# ==================== INSECURE HASHING TESTS ====================

def test_insecure_hash_positive():
    """CRYP-001: Using md5 for password"""
    code = '''
import hashlib
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert any('CRYP' in i.get('type', '') or 'md5' in i.get('description', '').lower() for i in issues), "Should detect md5"
    print("✓ CRYP-001 Positive: Detected")

def test_insecure_hash_negative():
    """CRYP: Secure with bcrypt"""
    code = '''
import bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert len(issues) == 0, "Should NOT detect (bcrypt)"
    print("✓ CRYP-001 Negative: Passed")


# ==================== SSRF TESTS ====================

def test_ssrf_positive():
    """SSRF-001: requests with user-controlled URL"""
    code = '''
import requests
def fetch_url(url):
    return requests.get(url)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert any('SSRF' in i.get('type', '') for i in issues), "Should detect SSRF"
    print("✓ SSRF-001 Positive: Detected")

def test_ssrf_negative():
    """SSRF: URL validation"""
    code = '''
import requests
from urllib.parse import urlparse
def fetch_url(url):
    parsed = urlparse(url)
    if parsed.domain not in ALLOWED_DOMAINS:
        raise ValueError("Invalid domain")
    return requests.get(url)
    '''
    result = detect_vulnerabilities(code)
    issues = result.get('issues', [])
    assert len(issues) == 0, "Should NOT detect (validated)"
    print("✓ SSRF-001 Negative: Passed")


# ==================== RUN ALL TESTS ====================

if __name__ == '__main__':
    print("=" * 60)
    print("AURIX UNIT TESTS")
    print("=" * 60)
    
    tests = [
        # SQL
        ('SQL-001 Positive', test_sql_001_positive),
        ('SQL-001 Negative', test_sql_001_negative),
        # OS/System
        ('OS-SYSTEM Positive', test_os_system_positive),
        ('OS-SYSTEM Negative', test_os_system_negative),
        # Path Traversal
        ('PATH-001 Positive', test_path_traversal_positive),
        ('PATH-001 Negative', test_path_traversal_negative),
        # Code Execution
        ('CODE-001 Positive', test_eval_positive),
        ('CODE-001 Negative', test_eval_negative),
        # Deserialization
        ('DESER-001 Positive', test_pickle_positive),
        ('DESER-001 Negative', test_pickle_negative),
        # YAML
        ('YAML-001 Positive', test_yaml_positive),
        ('YAML-001 Negative', test_yaml_negative),
        # Subprocess
        ('SUBPROCESS-001 Positive', test_subprocess_positive),
        ('SUBPROCESS-001 Negative', test_subprocess_negative),
        # Secrets
        ('SECRET-001 Positive', test_hardcoded_secret_positive),
        ('SECRET-001 Negative', test_hardcoded_secret_negative),
        # Crypto
        ('CRYP-001 Positive', test_insecure_hash_positive),
        ('CRYP-001 Negative', test_insecure_hash_negative),
        # SSRF
        ('SSRF-001 Positive', test_ssrf_positive),
        ('SSRF-001 Negative', test_ssrf_negative),
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
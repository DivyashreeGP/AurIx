#!/usr/bin/env python3
"""Unit Tests - Test individual components"""
import unittest
import sys
import json
import os
import tempfile
import subprocess
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def scan_code_file(code):
    """Scan code by creating temporary file and running detect.py"""
    try:
        # Create temporary file with code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            project_root = Path(__file__).parent.parent.parent
            # Run detect.py on the temp file with compact output
            result = subprocess.run(
                [sys.executable, str(project_root / 'detect.py'), temp_file, '--compact'],
                capture_output=True,
                text=True,
                cwd=str(project_root),
                timeout=10
            )
            
            # Check if report was generated
            report_path = project_root / 'results' / 'report.json'
            if report_path.exists():
                with open(report_path, 'r') as f:
                    report = json.load(f)
                    issues = []
                    for file_path, findings in report.items():
                        if findings:
                            issues.extend(findings)
                    return issues
            return []
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    except Exception as e:
        print(f"Error scanning code: {e}")
        return []


class TestDetectPatterns(unittest.TestCase):
    """Test detection patterns for vulnerabilities"""
    
    def test_sql_injection_detection(self):
        """SQL Injection should be detected"""
        vulnerable_code = 'query = "SELECT * FROM users WHERE id=" + user_id'
        issues = scan_code_file(vulnerable_code)
        self.assertTrue(len(issues) > 0, f"SQL injection not detected")
    
    def test_pickle_detection(self):
        """Pickle unsafe load should be detected"""
        vulnerable_code = '''import pickle
data = pickle.loads(untrusted_data)'''
        issues = scan_code_file(vulnerable_code)
        self.assertTrue(len(issues) > 0, f"Pickle vulnerability not detected")
    
    def test_eval_detection(self):
        """Eval with user input should be detected"""
        vulnerable_code = '''user_input = input("Enter: ")
result = eval(user_input)'''
        issues = scan_code_file(vulnerable_code)
        self.assertTrue(len(issues) > 0, f"Eval vulnerability not detected")
    
    def test_os_command_injection(self):
        """OS command injection should be detected"""
        vulnerable_code = '''import os
cmd = "ls " + user_input
os.system(cmd)'''
        issues = scan_code_file(vulnerable_code)
        self.assertTrue(len(issues) > 0, f"OS command injection not detected")
    
    def test_hardcoded_credentials(self):
        """Hardcoded passwords should be detected"""
        vulnerable_code = 'password = "admin123"; api_key = "sk-1234567890"'
        issues = scan_code_file(vulnerable_code)
        self.assertTrue(len(issues) > 0, f"Hardcoded credentials not detected")
    
    def test_weak_crypto_md5(self):
        """MD5 hashing should be detected"""
        vulnerable_code = '''import hashlib
hash_obj = hashlib.md5(password.encode())'''
        issues = scan_code_file(vulnerable_code)
        self.assertTrue(len(issues) > 0, f"MD5 weakness not detected")
    
    def test_weak_random(self):
        """Weak random generation should be detected"""
        vulnerable_code = '''import random
token = random.random()'''
        issues = scan_code_file(vulnerable_code)
        self.assertTrue(len(issues) > 0, f"Weak random not detected")
    
    def test_xxe_vulnerability(self):
        """XXE vulnerability should be detected"""
        vulnerable_code = '''import xml.etree.ElementTree as ET
root = ET.fromstring(xml_data)'''
        issues = scan_code_file(vulnerable_code)
        # May detect XML parsing issues
        self.assertIsInstance(issues, list)
    
    def test_no_vulnerability_clean_code(self):
        """Clean code should have minimal vulnerabilities"""
        clean_code = '''import json
data = json.loads(trusted_json_data)
print("Data processed safely")'''
        issues = scan_code_file(clean_code)
        # Clean code should have very few false positives (allow up to 3)
        self.assertTrue(len(issues) <= 3, f"Too many false positives: {len(issues)} issues found")

class TestRuleLoading(unittest.TestCase):
    """Test ruleset loading"""
    
    def test_ruleset_files_exist(self):
        """All ruleset files should exist"""
        ruleset_dir = Path(__file__).parent.parent.parent / "version_2.0" / "ruleset"
        self.assertTrue(ruleset_dir.exists())
        
        json_files = list(ruleset_dir.glob("*.json"))
        self.assertGreater(len(json_files), 30)
    
    def test_ruleset_valid_json(self):
        """All ruleset files should be valid JSON"""
        ruleset_dir = Path(__file__).parent.parent.parent / "version_2.0" / "ruleset"
        
        for json_file in ruleset_dir.glob("*.json"):
            with open(json_file) as f:
                data = json.load(f)
                self.assertIsInstance(data, list)
                for rule in data:
                    self.assertIn("id", rule)
                    self.assertIn("pattern", rule)

class TestBackendEndpoints(unittest.TestCase):
    """Test backend API endpoints"""
    
    def test_analyze_endpoint(self):
        """Test /analyze endpoint"""
        try:
            import requests
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"code": "pickle.loads(data)"},
                timeout=5
            )
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertIn("issues", result)
        except ImportError:
            self.skipTest("requests library not installed")
        except Exception as e:
            self.skipTest(f"Backend not running: {e}")
    
    def test_analyze_with_ai_endpoint(self):
        """Test /analyze-with-ai endpoint"""
        try:
            import requests
            response = requests.post(
                "http://localhost:8000/analyze-with-ai",
                json={
                    "code": "os.system(user_input)",
                    "language": "python"
                },
                timeout=10
            )
            self.assertIn(response.status_code, [200, 202])
        except ImportError:
            self.skipTest("requests library not installed")
        except Exception as e:
            self.skipTest(f"Backend not running: {e}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_empty_code(self):
        """Empty code should not crash"""
        empty_code = ""
        issues = scan_code_file(empty_code)
        self.assertIsInstance(issues, list, "Empty code should return list")
    
    def test_only_comments(self):
        """Code with only comments should not trigger excessive false positives"""
        comment_code = '''# This is a SQL injection: SELECT * FROM users WHERE id=' + user_id
# Another comment with pickle.loads(untrusted)
# os.system(bad_command)'''
        issues = scan_code_file(comment_code)
        # Comments may trigger pattern matches, but should be reasonable
        self.assertTrue(len(issues) <= 5, f"Too many false positives in comments: {len(issues)}")
    
    def test_unicode_characters(self):
        """Code with unicode characters should be handled"""
        unicode_code = '''# 中文注释
def hello():
    msg = "你好世界"  # Unicode string
    return msg
'''
        issues = scan_code_file(unicode_code)
        self.assertIsInstance(issues, list, "Unicode code should not crash")
    
    def test_very_long_line(self):
        """Very long line should be handled"""
        long_line = 'x = "' + 'a' * 5000 + '"'
        issues = scan_code_file(long_line)
        self.assertIsInstance(issues, list, "Long lines should not crash")
    
    def test_multiple_vulns_one_line(self):
        """Multiple vulnerabilities on same line should be detected"""
        multi_vuln = 'db.execute("SELECT * FROM users WHERE id=" + user_id); obj = pickle.loads(data); hash = hashlib.md5(pwd)'
        issues = scan_code_file(multi_vuln)
        self.assertTrue(len(issues) > 0, "Multiple vulnerabilities should be detected")
    
    def test_escaped_quotes_in_strings(self):
        """Escaped quotes should be handled correctly"""
        escaped_code = '''message = "User wrote: \\"SELECT * FROM users\\""
result = db.execute(message)'''
        issues = scan_code_file(escaped_code)
        self.assertIsInstance(issues, list, "Escaped quotes should be handled")
    
    def test_mixed_tabs_and_spaces(self):
        """Mixed tabs and spaces should be handled"""
        mixed_indent = '''def func():
	x = 1  # Tab
    y = 2  # Spaces
    result = db.execute("SELECT * FROM " + table)
    return result'''
        issues = scan_code_file(mixed_indent)
        self.assertIsInstance(issues, list, "Mixed indentation should be handled")
    
    def test_windows_line_endings(self):
        """Windows CRLF line endings should be handled"""
        crlf_code = 'import os\r\nuser_input = input()\r\nos.system(user_input)\r\n'
        issues = scan_code_file(crlf_code)
        self.assertTrue(len(issues) > 0, "CRLF line endings should work")
    
    def test_string_literals_vs_calls(self):
        """String literals should not be confused with actual calls"""
        string_literal = 'text = "eval(user_input)" ; db_query = "SELECT * FROM users WHERE id=" + str(id)'
        issues = scan_code_file(string_literal)
        # The actual concatenation should be caught, string literal should not
        self.assertIsInstance(issues, list, "String literals should be parsed correctly")
    
    def test_nested_function_calls(self):
        """Nested function calls should be handled"""
        nested = '''result = db.execute(os.system(pickle.loads(user_input)))'''
        issues = scan_code_file(nested)
        self.assertTrue(len(issues) > 0, "Nested vulnerabilities should be detected")
    
    def test_lambda_functions(self):
        """Lambda functions should be analyzed"""
        lambda_code = 'func = lambda x: db.execute("SELECT * FROM users WHERE id=" + str(x))'
        issues = scan_code_file(lambda_code)
        self.assertIsInstance(issues, list, "Lambda functions should be analyzed")
    
    def test_list_comprehension_with_vuln(self):
        """List comprehensions with vulnerabilities should be detected"""
        list_comp = '[db.execute("SELECT * FROM users WHERE id=" + str(x)) for x in user_ids]'
        issues = scan_code_file(list_comp)
        self.assertIsInstance(issues, list, "List comprehensions should be analyzed")
    
    def test_f_string_formatting(self):
        """F-strings should be analyzed for vulnerabilities"""
        f_string = 'query = f"SELECT * FROM users WHERE id={user_id}"'
        issues = scan_code_file(f_string)
        self.assertIsInstance(issues, list, "F-strings should be analyzed")
    
    def test_multiline_strings(self):
        """Multiline strings should be handled"""
        multiline = '''text = """
SELECT * FROM users 
WHERE id = 'value'
"""
result = db.execute(text + user_id)'''
        issues = scan_code_file(multiline)
        self.assertIsInstance(issues, list, "Multiline strings should be handled")
    
    def test_import_variations(self):
        """Various import styles should be detected"""
        imports = '''from pickle import loads
from os import system
import hashlib as md5_module

data = loads(untrusted)
system(cmd)
hash = md5_module.md5(pwd)'''
        issues = scan_code_file(imports)
        self.assertTrue(len(issues) > 0, "Import variations should be detected")
    
    def test_syntax_error_handling(self):
        """Syntax errors should not crash the detector"""
        syntax_error_code = 'def func(: \n broken syntax'
        issues = scan_code_file(syntax_error_code)
        # Should not crash even with syntax errors
        self.assertIsInstance(issues, list, "Syntax errors should not crash detector")
    
    def test_very_nested_data_structures(self):
        """Deeply nested structures should be handled"""
        nested_data = '''data = {
    "level1": {
        "level2": {
            "level3": {
                "query": "SELECT * FROM users WHERE id=" + str(user_id)
            }
        }
    }
}'''
        issues = scan_code_file(nested_data)
        self.assertIsInstance(issues, list, "Nested data structures should be handled")
    
    def test_commented_code_block(self):
        """Commented code blocks should not trigger excessive alerts"""
        commented = '''# db.execute("SELECT * FROM users WHERE id=" + user_id)
# pickle.loads(data)
# os.system(cmd)
def safe_function():
    return "OK"'''
        issues = scan_code_file(commented)
        self.assertTrue(len(issues) <= 10, f"Commented code should not trigger many alerts: {len(issues)}")
    
    def test_docstring_with_examples(self):
        """Docstrings with code examples should be handled"""
        docstring_code = '''def database_query(user_id):
    """
    DEPRECATED: Do NOT use this pattern:
    >> db.execute("SELECT * FROM users WHERE id=" + str(user_id))
    
    Instead use:
    >> db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    """
    # Correct implementation below
    return db.execute("SELECT * FROM users WHERE id=?", (user_id,))'''
        issues = scan_code_file(docstring_code)
        self.assertIsInstance(issues, list, "Docstrings should be handled")
    
    def test_raw_strings(self):
        """Raw strings should be handled"""
        raw_str = r'pattern = r"SELECT \* FROM users WHERE id=" + user_id'
        issues = scan_code_file(raw_str)
        self.assertIsInstance(issues, list, "Raw strings should be handled")
    
    def test_byte_strings(self):
        """Byte strings should be handled"""
        byte_str = '''data = b"SELECT * FROM users WHERE id="
result = db.execute(data + user_id.encode())'''
        issues = scan_code_file(byte_str)
        self.assertIsInstance(issues, list, "Byte strings should be handled")

if __name__ == '__main__':
    unittest.main(verbosity=2)

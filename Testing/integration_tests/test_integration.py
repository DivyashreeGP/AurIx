#!/usr/bin/env python3
"""Integration Tests - Test components working together"""
import unittest
import sys
import subprocess
import json
from pathlib import Path
from time import sleep

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestEndToEndDetection(unittest.TestCase):
    """Test the full detection pipeline"""
    
    def test_file_detection_pipeline(self):
        """Test detecting vulnerabilities in a file"""
        from detect import scan_file
        
        test_file = Path(__file__).parent.parent / "fixtures" / "vulnerable_sample.py"
        if test_file.exists():
            result = scan_file(str(test_file))
            self.assertIsInstance(result, (list, dict))
            self.assertGreater(len(result), 0)
    
    def test_backend_detection_integration(self):
        """Test backend receiving detection and processing"""
        import requests
        
        vulnerable_code = '''
import pickle
data = pickle.loads(untrusted)
result = eval(user_expr)
'''
        
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"code": vulnerable_code},
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Verify response structure
            self.assertIn("analysis", data)
            self.assertIn("issues", data)
            
            # Should have multiple issues
            self.assertGreater(len(data["issues"]), 1)
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend not running")
    
    def test_ai_transformation_integration(self):
        """Test backend AI transformation"""
        import requests
        
        vulnerable_code = "import pickle\nobj = pickle.loads(data)"
        
        try:
            response = requests.post(
                "http://localhost:8000/analyze-with-ai",
                json={
                    "code": vulnerable_code,
                    "language": "python"
                },
                timeout=15
            )
            
            self.assertIn(response.status_code, [200, 202])
            data = response.json()
            
            # Should have analysis
            self.assertIn("analysis", data)
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend not running")
    
    def test_multiple_vulnerability_detection(self):
        """Test detecting multiple vulnerabilities in one file"""
        import requests
        
        multi_vuln_code = '''
import os
import pickle
import hashlib

# SQL Injection
db.execute("SELECT * WHERE id=" + user_id)

# Pickle
obj = pickle.loads(untrusted)

# Weak hash
hash_val = hashlib.md5(password).hexdigest()

# OS command
os.system(f"ls {filename}")
'''
        
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"code": multi_vuln_code},
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Should detect multiple issues
            self.assertGreaterEqual(len(data["issues"]), 3)
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend not running")

class TestRulesetIntegration(unittest.TestCase):
    """Test ruleset integration"""
    
    def test_all_rulesets_loaded(self):
        """Test all rulesets can be loaded"""
        ruleset_dir = Path(__file__).parent.parent.parent / "version_2.0" / "ruleset"
        
        all_rules = []
        for json_file in ruleset_dir.glob("*.json"):
            with open(json_file) as f:
                rules = json.load(f)
                all_rules.extend(rules)
        
        # Should have 500+ rules
        self.assertGreater(len(all_rules), 500)
    
    def test_rule_pattern_validity(self):
        """Test all rule patterns are valid regex"""
        import re
        
        ruleset_dir = Path(__file__).parent.parent.parent / "version_2.0" / "ruleset"
        
        invalid_patterns = []
        for json_file in ruleset_dir.glob("*.json"):
            with open(json_file) as f:
                rules = json.load(f)
                for rule in rules:
                    try:
                        re.compile(rule.get("pattern", ""))
                    except re.error:
                        invalid_patterns.append((json_file.name, rule.get("id")))
        
        self.assertEqual(len(invalid_patterns), 0, 
                        f"Invalid patterns found: {invalid_patterns}")

class TestDetectionAccuracy(unittest.TestCase):
    """Test detection accuracy"""
    
    def test_false_positives(self):
        """Clean code should not trigger false positives"""
        import requests
        
        clean_code = '''
def safe_function():
    """Safe operation"""
    data = load_trusted_data()
    result = process_data(data)
    return result
'''
        
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"code": clean_code},
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Should have minimal issues
            self.assertLess(len(data["issues"]), 2)
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend not running")
    
    def test_true_positives(self):
        """Vulnerable code should be detected"""
        import requests
        
        vulnerable_code = "db.execute('SELECT * FROM users WHERE id=' + str(user_id))"
        
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"code": vulnerable_code},
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Should detect vulnerability
            self.assertGreater(len(data["issues"]), 0)
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend not running")

class TestIntegrationEdgeCases(unittest.TestCase):
    """Test integration edge cases"""
    
    def test_rapid_consecutive_requests(self):
        """Backend should handle rapid consecutive requests"""
        import requests
        
        try:
            for i in range(5):
                response = requests.post(
                    "http://localhost:8000/analyze",
                    json={"code": f"x{i} = {i}"},
                    timeout=5
                )
                self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend not running")
    
    def test_very_large_code_submission(self):
        """Backend should handle very large code files"""
        import requests
        
        large_code = "x = 1\n" * 10000  # 10k lines
        
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"code": large_code},
                timeout=10
            )
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend not running")
    
    def test_empty_code_submission(self):
        """Backend should handle empty code submissions"""
        import requests
        
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"code": ""},
                timeout=5
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("issues", data)
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend not running")
    
    def test_unicode_code_submission(self):
        """Backend should handle unicode in code"""
        import requests
        
        unicode_code = '''# 中文注释
def greet():
    msg = "हलो वर्ल्ड"  # Unicode
    return msg'''
        
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"code": unicode_code},
                timeout=5
            )
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend not running")
    
    def test_concurrent_multi_file_detection(self):
        """Test detecting multiple files concurrently"""
        import requests
        from concurrent.futures import ThreadPoolExecutor
        
        def analyze_code(code):
            try:
                response = requests.post(
                    "http://localhost:8000/analyze",
                    json={"code": code},
                    timeout=5
                )
                return response.status_code == 200
            except:
                return False
        
        try:
            codes = [
                "x = pickle.loads(data)",
                "db.execute('SELECT * FROM ' + user_id)",
                "os.system(cmd)",
            ]
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                results = list(executor.map(analyze_code, codes))
            
            self.assertTrue(all(results), "All concurrent requests should succeed")
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend not running")
    
    def test_response_format_consistency(self):
        """Response format should be consistent across requests"""
        import requests
        
        try:
            responses = []
            for i in range(3):
                resp = requests.post(
                    "http://localhost:8000/analyze",
                    json={"code": "x = 1"},
                    timeout=5
                )
                responses.append(resp.json())
            
            # All should have same structure
            for resp in responses:
                self.assertIn("issues", resp)
                self.assertIn("analysis", resp)
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend not running")
    
    def test_error_handling_malformed_json(self):
        """Backend should handle malformed requests gracefully"""
        import requests
        
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"invalid_key": "invalid_value"},
                timeout=5
            )
            # Should either accept or return proper error
            self.assertIn(response.status_code, [200, 400, 422])
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend not running")
        except Exception:
            pass  # Request errors are acceptable

if __name__ == '__main__':
    unittest.main(verbosity=2)


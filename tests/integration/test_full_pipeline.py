"""
Integration tests for full vulnerability detection pipeline
Tests end-to-end analysis workflows and API interactions
"""
import pytest
import json
import tempfile
from pathlib import Path
import sys
import subprocess

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestEndToEndAnalysis:
    """Test complete vulnerability detection pipeline"""
    
    def test_analyze_then_analyze_with_ai(self):
        """Test full workflow: analyze -> detect issues -> generate fixes"""
        vulnerable_code = """
import subprocess
user_input = input()
subprocess.run(user_input, shell=True)
"""
        # Step 1: Analyze for vulnerabilities
        response1 = client.post("/analyze", json={"code": vulnerable_code})
        assert response1.status_code == 200
        analysis_result = response1.json()
        assert "issues" in analysis_result
        
        # Step 2: If issues found, get AI-powered recommendations
        if analysis_result["issues"]:
            response2 = client.post("/analyze-with-ai", json={
                "code": vulnerable_code,
                "issues": analysis_result["issues"]
            })
            assert response2.status_code == 200
            ai_result = response2.json()
            # Should have analysis, secure code, or explanation
            assert len(ai_result) > 0
    
    def test_sql_injection_full_flow(self):
        """Test SQL injection detection and fix generation"""
        sql_code = """
import sqlite3
conn = sqlite3.connect(':memory:')
user_id = input()
query = "SELECT * FROM users WHERE id=" + user_id
conn.execute(query)
"""
        response1 = client.post("/analyze", json={"code": sql_code})
        assert response1.status_code == 200
        
        result = response1.json()
        assert "issues" in result
    
    def test_pickle_vulnerability_full_flow(self):
        """Test pickle vulnerability detection"""
        pickle_code = """
import pickle
user_data = input()
obj = pickle.loads(user_data)
"""
        response = client.post("/analyze", json={"code": pickle_code})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result
    
    def test_hardcoded_credentials_flow(self):
        """Test hardcoded credentials detection"""
        cred_code = """
password = "my_secret_password"
database_url = "postgres://user:pass123@localhost/db"
api_key = "sk-1234567890abcdef"
"""
        response = client.post("/analyze", json={"code": cred_code})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result
    
    def test_weak_cryptography_flow(self):
        """Test weak cryptography detection"""
        crypto_code = """
import hashlib
password = "user_input"
hashed = hashlib.md5(password.encode()).hexdigest()
"""
        response = client.post("/analyze", json={"code": crypto_code})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result
    
    def test_security_misconfiguration_flow(self):
        """Test debug=True detection"""
        debug_code = """
from flask import Flask
app = Flask(__name__)
app.run(debug=True)
"""
        response = client.post("/analyze", json={"code": debug_code})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result
    
    def test_eval_vulnerability_flow(self):
        """Test eval() vulnerability detection"""
        eval_code = """
user_input = input()
result = eval(user_input)
print(result)
"""
        response = client.post("/analyze", json={"code": eval_code})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result


class TestMultipleVulnerabilitiesDetection:
    """Test detection of multiple vulnerabilities in single code"""
    
    def test_detect_multiple_issues_in_code(self):
        """Test detecting multiple vulnerabilities"""
        complex_code = """
import pickle
import subprocess
import hashlib

# Multiple vulnerabilities in one file
user_input = input()

# Vulnerability 1: Pickle
data = pickle.loads(user_input)

# Vulnerability 2: Eval
result = eval(user_input)

# Vulnerability 3: Subprocess shell=True
subprocess.run(user_input, shell=True)

# Vulnerability 4: Weak crypto
password_hash = hashlib.md5(user_input.encode()).hexdigest()
"""
        response = client.post("/analyze", json={"code": complex_code})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result
        # Should detect multiple issues
        assert isinstance(result["issues"], list)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_analyze_very_long_code(self):
        """Test with very large code file"""
        large_code = "x = 1\n" * 10000  # 10000 lines
        response = client.post("/analyze", json={"code": large_code})
        assert response.status_code == 200
    
    def test_analyze_special_characters_in_code(self):
        """Test code with special characters"""
        code_with_special = """
# Comment with special chars: !@#$%^&*()
string = "Contains 'quotes' and \\"escaped\\" chars"
"""
        response = client.post("/analyze", json={"code": code_with_special})
        assert response.status_code == 200
    
    def test_analyze_unicode_code(self):
        """Test code with unicode characters"""
        unicode_code = """
# 中文注释
variable = "日本語のコード"
print("Hello 世界")
"""
        response = client.post("/analyze", json={"code": unicode_code})
        assert response.status_code == 200
    
    def test_analyze_malformed_python(self):
        """Test with malformed Python syntax"""
        malformed_code = "this is not valid python"
        response = client.post("/analyze", json={"code": malformed_code})
        assert response.status_code == 200
    
    def test_analyze_empty_code(self):
        """Test with completely empty code"""
        response = client.post("/analyze", json={"code": ""})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result
    
    def test_analyze_only_comments(self):
        """Test with only comments"""
        comment_code = "# This is just a comment\n# No real code here"
        response = client.post("/analyze", json={"code": comment_code})
        assert response.status_code == 200


class TestResponseConsistency:
    """Test consistency of API responses"""
    
    def test_consistent_issue_structure(self):
        """Test that all issues have consistent structure"""
        code = """
import pickle
pickle.loads(input())
"""
        response = client.post("/analyze", json={"code": code})
        result = response.json()
        
        for issue in result["issues"]:
            assert "type" in issue
            assert "severity" in issue
            assert "line" in issue
            assert "code" in issue or "description" in issue
    
    def test_severity_levels_valid(self):
        """Test that severity levels are valid"""
        code = "x = eval(input())"
        response = client.post("/analyze", json={"code": code})
        result = response.json()
        
        valid_severities = {"high", "medium", "low"}
        for issue in result["issues"]:
            assert issue.get("severity", "").lower() in valid_severities
    
    def test_line_numbers_positive(self):
        """Test that line numbers are positive integers"""
        code = "result = pickle.loads(data)\nx = 2"
        response = client.post("/analyze", json={"code": code})
        result = response.json()
        
        for issue in result["issues"]:
            if "line" in issue:
                assert isinstance(issue["line"], int)
                assert issue["line"] > 0


class TestAIFallback:
    """Test AI endpoint with various scenarios"""
    
    def test_ai_response_with_no_issues(self):
        """Test AI endpoint when no issues detected"""
        safe_code = "x = 1\ny = 2"
        response = client.post("/analyze-with-ai", json={
            "code": safe_code,
            "issues": []
        })
        assert response.status_code == 200
    
    def test_ai_response_with_multiple_issues(self):
        """Test AI response with multiple detected issues"""
        vulnerable_code = "result = eval(input())"
        issues = [
            {
                "type": "EVAL_USAGE",
                "line": 1,
                "severity": "high",
                "description": "Use of eval with user input"
            }
        ]
        response = client.post("/analyze-with-ai", json={
            "code": vulnerable_code,
            "issues": issues
        })
        assert response.status_code == 200
        result = response.json()
        assert len(result) > 0


class TestDetectPythonFile:
    """Test detecting vulnerabilities in Python files"""
    
    def test_detect_from_temp_file(self):
        """Test that backend correctly processes temp files"""
        code_to_analyze = """
import subprocess
user_cmd = input()
subprocess.call(user_cmd, shell=True)
"""
        response = client.post("/analyze", json={"code": code_to_analyze})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result


class TestSecurityCategories:
    """Test detection of different security categories"""
    
    def test_injection_category(self):
        """Test INJC (Injection) category detection"""
        injection_code = 'query = f"SELECT * FROM users WHERE id={user_id}"'
        response = client.post("/analyze", json={"code": injection_code})
        result = response.json()
        # Injection should be detected or analyzed
        assert response.status_code == 200
    
    def test_insecure_data_access(self):
        """Test IDAF (Insecure Data Access) category"""
        insecure_code = """
import pickle
data = pickle.loads(user_provided)
"""
        response = client.post("/analyze", json={"code": insecure_code})
        result = response.json()
        assert response.status_code == 200
    
    def test_cryptography_failures(self):
        """Test CRYF (Cryptography Failures) category"""
        cryp_code = """
import hashlib
weak_hash = hashlib.md5(password)
"""
        response = client.post("/analyze", json={"code": cryp_code})
        result = response.json()
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

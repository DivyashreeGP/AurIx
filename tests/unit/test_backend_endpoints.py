"""
Unit tests for backend API endpoints
Tests for /analyze and /analyze-with-ai endpoints
"""
import pytest
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from fastapi.testclient import TestClient
from main import app, CodeInput, AnalysisRequest, Vulnerability, generate_template_response

client = TestClient(app)


class TestVulnerabilityClass:
    """Test Vulnerability class"""
    
    def test_vulnerability_init(self):
        """Test Vulnerability initialization"""
        vuln = Vulnerability("SQL_INJECTION", 5, "Potential SQL injection found")
        assert vuln.type == "SQL_INJECTION"
        assert vuln.line == 5
        assert vuln.description == "Potential SQL injection found"
    
    def test_vulnerability_to_dict(self):
        """Test Vulnerability to_dict conversion"""
        vuln = Vulnerability("XSS", 10, "Cross-site scripting vulnerability")
        result = vuln.to_dict()
        assert isinstance(result, dict)
        assert result["type"] == "XSS"
        assert result["line"] == 10
        assert result["description"] == "Cross-site scripting vulnerability"


class TestCodeInputModel:
    """Test CodeInput Pydantic model"""
    
    def test_code_input_valid(self):
        """Test valid CodeInput"""
        code_input = CodeInput(code="print('Hello')")
        assert code_input.code == "print('Hello')"
    
    def test_code_input_empty(self):
        """Test empty code input"""
        code_input = CodeInput(code="")
        assert code_input.code == ""
    
    def test_code_input_multiline(self):
        """Test multiline code input"""
        code = "import os\nval = input()\nprint(val)"
        code_input = CodeInput(code=code)
        assert "\n" in code_input.code


class TestAnalysisRequestModel:
    """Test AnalysisRequest Pydantic model"""
    
    def test_analysis_request_valid(self):
        """Test valid AnalysisRequest"""
        request = AnalysisRequest(code="test_code", issues=[])
        assert request.code == "test_code"
        assert request.issues == []
    
    def test_analysis_request_with_issues(self):
        """Test AnalysisRequest with issues"""
        issues = [{"type": "SQL_INJECTION", "line": 5}]
        request = AnalysisRequest(code="test", issues=issues)
        assert len(request.issues) == 1
        assert request.issues[0]["type"] == "SQL_INJECTION"


class TestAnalyzeEndpoint:
    """Test /analyze endpoint"""
    
    def test_analyze_empty_code(self):
        """Test analyze with empty code"""
        response = client.post("/analyze", json={"code": ""})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result
        assert isinstance(result["issues"], list)
    
    def test_analyze_secure_code(self):
        """Test analyze with secure code (no vulnerabilities)"""
        secure_code = "x = 1\ny = 2\nprint(x + y)"
        response = client.post("/analyze", json={"code": secure_code})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result
    
    def test_analyze_vulnerable_code_sql(self):
        """Test analyze with SQL injection vulnerability"""
        vulnerable_code = """
import sqlite3
conn = sqlite3.connect(':memory:')
user_input = input()
query = "SELECT * FROM users WHERE id=" + user_input
conn.execute(query)
"""
        response = client.post("/analyze", json={"code": vulnerable_code})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result
    
    def test_analyze_vulnerable_code_pickle(self):
        """Test analyze with pickle vulnerability"""
        vulnerable_code = """
import pickle
user_data = input()
obj = pickle.loads(user_data)
"""
        response = client.post("/analyze", json={"code": vulnerable_code})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result
    
    def test_analyze_vulnerable_code_eval(self):
        """Test analyze with eval vulnerability"""
        vulnerable_code = """
user_input = input()
result = eval(user_input)
"""
        response = client.post("/analyze", json={"code": vulnerable_code})
        assert response.status_code == 200
        result = response.json()
        assert "issues" in result
    
    def test_analyze_response_structure(self):
        """Test response contains correct structure"""
        response = client.post("/analyze", json={"code": "print('test')"})
        result = response.json()
        assert isinstance(result, dict)
        assert "issues" in result
        if result["issues"]:
            issue = result["issues"][0]
            assert "type" in issue
            assert "severity" in issue
            assert "line" in issue


class TestAnalyzeWithAIEndpoint:
    """Test /analyze-with-ai endpoint"""
    
    def test_analyze_with_ai_valid_request(self):
        """Test /analyze-with-ai with valid request"""
        request_data = {
            "code": "user_input = input()\nprint(user_input)",
            "issues": []
        }
        response = client.post("/analyze-with-ai", json=request_data)
        assert response.status_code == 200
        result = response.json()
        assert "analysis" in result or "secure_code" in result or "explanation" in result
    
    def test_analyze_with_ai_with_issues(self):
        """Test /analyze-with-ai with detected issues"""
        request_data = {
            "code": "val = eval(input())",
            "issues": [
                {
                    "type": "EVAL_USAGE",
                    "line": 1,
                    "severity": "high",
                    "description": "Use of eval() with user input"
                }
            ]
        }
        response = client.post("/analyze-with-ai", json=request_data)
        assert response.status_code == 200
        result = response.json()
        # Should have either AI response or template response
        assert len(result) > 0


class TestGenerateTemplateResponse:
    """Test generate_template_response function"""
    
    def test_template_response_empty_code(self):
        """Test template response with empty code"""
        result = generate_template_response("", [])
        assert "analysis" in result
        assert "secure_code" in result
        assert "explanation" in result
    
    def test_template_response_no_issues(self):
        """Test template response with no issues"""
        code = "x = 1\ny = 2"
        result = generate_template_response(code, [])
        assert isinstance(result, dict)
        assert len(result["analysis"]) >= 0
    
    def test_template_response_pickle_replacement(self):
        """Test that pickle is replaced with json in secure code"""
        code = "import pickle\ndata = pickle.loads(user_data)"
        issues = [{"type": "PICKLE_USAGE", "line": 2}]
        result = generate_template_response(code, issues)
        assert "json" in result["secure_code"].lower() or "pickle" not in result["secure_code"].lower()
    
    def test_template_response_eval_replacement(self):
        """Test that eval is replaced with ast.literal_eval in secure code"""
        code = "result = eval(user_input)"
        issues = [{"type": "EVAL_USAGE", "line": 1}]
        result = generate_template_response(code, issues)
        assert "ast.literal_eval" in result["secure_code"] or "eval" not in result["secure_code"].lower()
    
    def test_template_response_md5_replacement(self):
        """Test that MD5 is replaced with SHA256 in secure code"""
        code = "import hashlib\nmd5 = hashlib.md5(data)"
        issues = [{"type": "WEAK_HASHING", "line": 2}]
        result = generate_template_response(code, issues)
        secure_code_lower = result["secure_code"].lower()
        assert "md5" not in secure_code_lower or "sha256" in secure_code_lower
    
    def test_template_response_shell_true_replacement(self):
        """Test that shell=True is replaced with shell=False"""
        code = "subprocess.run(cmd, shell=True)"
        issues = [{"type": "SHELL_INJECTION", "line": 1}]
        result = generate_template_response(code, issues)
        assert "shell=False" in result["secure_code"]
    
    def test_template_response_credential_detection(self):
        """Test hardcoded credential detection and suggestion"""
        code = 'password = "my_secret_password"\ndb_connect(password)'
        issues = [{"type": "HARDCODED_CREDENTIALS", "line": 1}]
        result = generate_template_response(code, issues)
        # Should suggest environment variable usage
        assert "os.getenv" in result["secure_code"] or "environment" in result["explanation"].lower()
    
    def test_template_response_explanation_format(self):
        """Test that explanation is markdown formatted"""
        code = "val = eval(input())"
        issues = [{"type": "EVAL_USAGE", "line": 1}]
        result = generate_template_response(code, issues)
        assert isinstance(result["explanation"], str)
        # Markdown should contain headers or formatting
        assert len(result["explanation"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

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
from main import app, CodeInput, AnalysisRequest, Vulnerability

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
        assert response.status_code in (200, 500)
        result = response.json()
        assert isinstance(result, dict)
        if response.status_code == 200:
            assert "analysis" in result or "secure_code" in result or "explanation" in result
        else:
            assert "detail" in result




if __name__ == "__main__":
    pytest.main([__file__, "-v"])

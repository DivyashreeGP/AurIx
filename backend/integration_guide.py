"""
integration_guide.py
How to integrate secure code generation with FastAPI backend
"""

# ===== FASTAPI MODELS (Pydantic) =====

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class VulnerabilityTypeEnum(str, Enum):
    SQL_INJECTION = "SQL Injection"
    PICKLE_VULNERABILITY = "Pickle Vulnerability"
    EVAL_USAGE = "Eval Usage"
    HARDCODED_CREDENTIALS = "Hardcoded Credentials"
    WEAK_CRYPTOGRAPHY = "Weak Cryptography"
    DEBUG_MODE = "Debug Mode Enabled"


class SeverityEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class CodeExampleResponse(BaseModel):
    """Single secure code example"""
    title: str
    method: str
    code: str
    language: str = "python"


class VulnerabilityDetailResponse(BaseModel):
    """Complete vulnerability detail with secure code"""
    
    # Basic info
    id: str
    type: VulnerabilityTypeEnum
    severity: SeverityEnum
    line_number: int
    file_path: Optional[str] = None
    
    # Code and explanation
    original_code: str = Field(..., description="The vulnerable code line")
    vulnerability_explanation: str
    risk: str
    
    # How to fix (step-by-step)
    how_to_fix: List[str]
    
    # Secure code reference
    secure_code_examples: List[CodeExampleResponse] = Field(
        description="Multiple secure code options"
    )
    
    # Warning and disclaimer
    security_warning: str = Field(
        default="Even with these secure code examples, security also depends on proper input validation, error handling, database permissions, regular updates, and professional security audits. 100% SECURITY CANNOT BE GUARANTEED."
    )
    
    # In case no secure code exists
    secure_code_generated: bool = True
    no_code_message: Optional[str] = None


class BulkVulnerabilityResponse(BaseModel):
    """Multiple vulnerabilities with secure code"""
    total_vulnerabilities: int
    vulnerabilities: List[VulnerabilityDetailResponse]
    processing_time_ms: float


# ===== FASTAPI ROUTES =====

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import datetime
import time
from secure_code_generator import generate_secure_code, VulnerabilityType

router = APIRouter(prefix="/api/v1/vulnerabilities", tags=["vulnerabilities"])


@router.get("/detect", response_model=BulkVulnerabilityResponse)
async def detect_vulnerabilities_with_secure_code(
    file_path: str = Query(..., description="Path to Python file to analyze"),
    include_secure_code: bool = Query(True, description="Include secure code examples")
):
    """
    Detect vulnerabilities and return secure code suggestions
    
    Example:
        GET /api/v1/vulnerabilities/detect?file_path=app.py&include_secure_code=true
    """
    start_time = time.time()
    
    try:
        # Your existing vulnerability detection logic here
        vulns = detect_vulnerabilities(file_path)
        
        responses = []
        for vuln in vulns:
            # Generate secure code for each vulnerability
            secure_suggestion = generate_secure_code(
                VulnerabilityType(vuln['type']),
                vuln['code']
            )
            
            # Build response
            response = VulnerabilityDetailResponse(
                id=f"{file_path}:{vuln['line']}:{vuln['type']}",
                type=VulnerabilityTypeEnum(vuln['type']),
                severity=SeverityEnum(vuln.get('severity', 'MEDIUM')),
                line_number=vuln['line'],
                file_path=file_path,
                original_code=vuln['code'],
                vulnerability_explanation=secure_suggestion.explanation,
                risk=secure_suggestion.risk,
                how_to_fix=secure_suggestion.how_to_fix,
                secure_code_examples=[
                    CodeExampleResponse(
                        title=ex.title,
                        method=ex.method,
                        code=ex.code,
                        language=ex.language
                    )
                    for ex in secure_suggestion.secure_code_examples
                ],
                secure_code_generated=len(secure_suggestion.secure_code_examples) > 0,
                no_code_message=secure_suggestion.no_code_message
            )
            responses.append(response)
        
        processing_time = (time.time() - start_time) * 1000
        
        return BulkVulnerabilityResponse(
            total_vulnerabilities=len(responses),
            vulnerabilities=responses,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting vulnerabilities: {str(e)}")


@router.get("/detail/{vuln_id}", response_model=VulnerabilityDetailResponse)
async def get_vulnerability_detail(
    vuln_id: str,
    include_secure_code: bool = Query(True)
):
    """
    Get detailed information about a specific vulnerability with secure code
    
    Example:
        GET /api/v1/vulnerabilities/detail/app.py:45:SQL%20Injection
    """
    
    try:
        # Parse vuln_id format: "file:line:type"
        parts = vuln_id.split(':')
        if len(parts) < 3:
            raise ValueError("Invalid vulnerability ID format")
        
        file_path = parts[0]
        line_num = int(parts[1])
        vuln_type = parts[2]
        
        # Fetch vulnerability details from database/cache
        vuln_data = get_vulnerability_by_id(vuln_id)
        
        if not vuln_data:
            raise HTTPException(status_code=404, detail="Vulnerability not found")
        
        # Generate secure code
        secure_suggestion = generate_secure_code(
            VulnerabilityType(vuln_type),
            vuln_data['code']
        )
        
        return VulnerabilityDetailResponse(
            id=vuln_id,
            type=VulnerabilityTypeEnum(vuln_type),
            severity=SeverityEnum(vuln_data.get('severity', 'MEDIUM')),
            line_number=line_num,
            file_path=file_path,
            original_code=vuln_data['code'],
            vulnerability_explanation=secure_suggestion.explanation,
            risk=secure_suggestion.risk,
            how_to_fix=secure_suggestion.how_to_fix,
            secure_code_examples=[
                CodeExampleResponse(
                    title=ex.title,
                    method=ex.method,
                    code=ex.code,
                    language=ex.language
                )
                for ex in secure_suggestion.secure_code_examples
            ],
            secure_code_generated=len(secure_suggestion.secure_code_examples) > 0,
            no_code_message=secure_suggestion.no_code_message
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching vulnerability: {str(e)}")


# ===== INTEGRATION EXAMPLE =====

"""
Usage in your FastAPI application:

from fastapi import FastAPI
from integration_guide import router as vuln_router

app = FastAPI(title="AurIx - Vulnerability Detection")

# Include routes
app.include_router(vuln_router)

# Example response from /api/v1/vulnerabilities/detect:
{
  "total_vulnerabilities": 1,
  "processing_time_ms": 45.23,
  "vulnerabilities": [
    {
      "id": "app.py:45:SQL Injection",
      "type": "SQL Injection",
      "severity": "CRITICAL",
      "line_number": 45,
      "file_path": "app.py",
      "original_code": "query = 'SELECT * FROM users WHERE id=' + user_input",
      "vulnerability_explanation": "Direct string concatenation with user input allows SQL injection attacks",
      "risk": "Attacker can bypass query logic, extract/modify data, or execute arbitrary SQL",
      "how_to_fix": [
        "Use parameterized queries (prepared statements)",
        "Never concatenate user input into SQL directly",
        "Validate and sanitize input types and lengths",
        "Use ORM frameworks (SQLAlchemy, Django ORM)",
        "Apply principle of least privilege to database users",
        "Implement query result length limits"
      ],
      "secure_code_examples": [
        {
          "title": "Method 1: Parameterized Query (sqlite3)",
          "method": "Using ? placeholders with execute()",
          "code": "cursor.execute(\"SELECT * FROM users WHERE id=?\", (user_id,))\\nresult = cursor.fetchone()",
          "language": "python"
        },
        {
          "title": "Method 2: Named Parameters (PostgreSQL)",
          "method": "Using named placeholders for clarity",
          "code": "cursor.execute(\\n    \"SELECT * FROM users WHERE id=%(user_id)s AND email=%(email)s\",\\n    {\"user_id\": user_id, \"email\": user_email}\\n)\\nresult = cursor.fetchone()",
          "language": "python"
        },
        ...more examples...
      ],
      "security_warning": "Even with these secure code examples, security also depends on proper input validation, error handling, database permissions, regular updates, and professional security audits. 100% SECURITY CANNOT BE GUARANTEED.",
      "secure_code_generated": true,
      "no_code_message": null
    }
  ]
}
"""


# ===== FRONTEND USAGE EXAMPLE =====

"""
React component using the API:

import React, { useState, useEffect } from 'react';
import VulnerabilityDetailComponent from './components/VulnerabilityDetailComponent';

function VulnerabilityViewer() {
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState('');

  const fetchVulnerabilities = async (filePath) => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/v1/vulnerabilities/detect?file_path=${filePath}&include_secure_code=true`
      );
      const data = await response.json();
      setVulnerabilities(data.vulnerabilities);
    } catch (error) {
      console.error('Error fetching vulnerabilities:', error);
    }
    setLoading(false);
  };

  return (
    <div className="vulnerability-viewer">
      <input
        type="text"
        placeholder="Enter file path"
        value={selectedFile}
        onChange={(e) => setSelectedFile(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && fetchVulnerabilities(selectedFile)}
      />
      
      <button onClick={() => fetchVulnerabilities(selectedFile)}>
        Analyze
      </button>

      {loading && <p>Analyzing...</p>}

      {vulnerabilities.map((vuln) => (
        <VulnerabilityDetailComponent
          key={vuln.id}
          vulnerability={{
            type: vuln.type,
            severity: vuln.severity,
            line_number: vuln.line_number,
            original_code: vuln.original_code,
            explanation: vuln.vulnerability_explanation,
            risk: vuln.risk,
            how_to_fix: vuln.how_to_fix,
            secure_code_examples: vuln.secure_code_examples,
            no_code_message: vuln.no_code_message
          }}
        />
      ))}
    </div>
  );
}

export default VulnerabilityViewer;
"""


# ===== TESTING THE INTEGRATION =====

"""
Unit test example:

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_detect_sql_injection():
    response = client.get(
        "/api/v1/vulnerabilities/detect",
        params={"file_path": "test_sql.py"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_vulnerabilities"] >= 1
    vuln = data["vulnerabilities"][0]
    
    assert vuln["type"] == "SQL Injection"
    assert vuln["severity"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    assert len(vuln["how_to_fix"]) > 0
    assert len(vuln["secure_code_examples"]) > 0
    assert vuln["secure_code_generated"] == True

def test_secure_code_generated():
    response = client.get(
        "/api/v1/vulnerabilities/detect",
        params={"file_path": "test_sql.py", "include_secure_code": True}
    )
    
    data = response.json()
    for vuln in data["vulnerabilities"]:
        # Check all required fields are present
        assert "original_code" in vuln
        assert "vulnerability_explanation" in vuln
        assert "how_to_fix" in vuln
        assert "secure_code_examples" in vuln
        assert "security_warning" in vuln
        
        # Check examples have code
        for example in vuln["secure_code_examples"]:
            assert "title" in example
            assert "code" in example
            assert len(example["code"]) > 0
"""


print("✅ Integration guide created successfully!")
print("\nNext steps:")
print("1. Add secure_code_generator.py to your backend")
print("2. Update your API routes with the examples above")
print("3. Update your FastAPI models to include SecureCodeResponse")
print("4. Test with the unit test examples")
print("5. Deploy and test the frontend component")

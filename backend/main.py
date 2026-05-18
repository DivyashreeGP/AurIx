from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import subprocess
import json
import uuid
import sys
import tempfile
from pathlib import Path

# ================================
# AI ENGINE IMPORT SETUP
# ================================

ai_engine_path = Path(__file__).resolve().parent.parent / "gemini_ai_reasoning_engine"
sys.path.insert(0, str(ai_engine_path.parent))

class Vulnerability:
    def __init__(self, vuln_type: str, line: int, description: str):
        self.type = vuln_type
        self.line = line
        self.description = description

    def to_dict(self):
        return {
            "type": self.type,
            "line": self.line,
            "description": self.description,
        }

try:
    from gemini_ai_reasoning_engine.app.reasoning import generate_explanation
    from gemini_ai_reasoning_engine.app.secure_generator import generate_secure_code
    LOCAL_AI_AVAILABLE = True
    print("✓ AI Engine loaded")
except Exception as e:
    print(f"⚠ AI Engine not available: {e}")
    LOCAL_AI_AVAILABLE = False

# ================================
# FASTAPI INIT
# ================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠ Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# REQUEST MODELS
# ================================

class CodeInput(BaseModel):
    code: str = Field(..., min_length=0, max_length=50000)

class AnalysisRequest(BaseModel):
    code: str
    issues: list

# ================================
# CONSTANT MAPPINGS
# ================================

severity_mapping = {
    "INJC": "high",
    "IDAF": "high",
    "SDIF": "high",
    "CRYF": "high",
    "CRYP": "high",
    "SECM": "medium",
    "BRAC": "high",
}

type_mapping = {
    "SQL": "SQL Injection",
    "SUBPROCESS": "Command Injection",
    "SUBPROC": "Command Injection",
    "CREDENTIALS": "Hard-coded Credentials",
    "PICKLE": "Insecure Deserialization",
    "EVAL": "Code Injection",
    "WITH-OPEN": "Path Traversal",
    "MD5": "Weak Cryptography",
    "ELEMENTTREE": "XXE",
    "RANDOM": "Weak Random Generation",
    "REQUEST": "Broken Access Control",
    "DEBUG": "Security Misconfiguration",
}

# ================================
# /analyze ENDPOINT
# ================================

@app.post("/analyze")
def analyze(data: CodeInput):
    code = data.code

    root = Path(__file__).resolve().parent.parent

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(code.encode("utf-8"))
            temp_file_path = Path(temp_file.name)

        out_file = root / "results" / f"temp_{uuid.uuid4()}.json"
        out_file.parent.mkdir(parents=True, exist_ok=True)

        # Run detection engine safely
        result = subprocess.run(
            [
                sys.executable,
                str(root / "detect.py"),
                str(temp_file_path),
                "--only-issues",
                "--compact",
                "-o",
                str(out_file)
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Detection engine failed: {result.stderr}"
            )

        if not out_file.exists():
            return {"issues": []}

        data_json = json.loads(out_file.read_text(encoding="utf-8"))

        issues = []
        seen = set()

        for file in data_json:
            for item in data_json[file]:

                reported_line = item.get("line", 1)
                try:
                    line = int(reported_line)
                except (TypeError, ValueError):
                    line = 1

                categories = item.get("categories", [])
                rules = item.get("rules", [])
                code_snippet = item.get("code", "")

                primary_category = categories[0] if categories else "SECM"
                severity = severity_mapping.get(primary_category, "medium")

                type_name = "Security Vulnerability"
                for rule in rules:
                    for key, value in type_mapping.items():
                        if key in rule:
                            type_name = value
                            break
                    if type_name != "Security Vulnerability":
                        break

                description = (
                    f"{', '.join(categories)} - {code_snippet[:60]}"
                    if code_snippet else ", ".join(categories)
                )

                # Deduplicate by line, type, and description
                signature = (line, type_name, description)
                if signature not in seen:
                    seen.add(signature)
                    issues.append({
                        "type": type_name,
                        "description": description,
                        "severity": severity,
                        "line": line,
                        "column": 1,
                        "code": code_snippet,
                        "rules": rules,
                        "categories": categories
                    })

        return {"issues": issues}

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Detection timed out")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        try:
            temp_file_path.unlink(missing_ok=True)
            if out_file.exists():
                out_file.unlink()
        except:
            pass

# ================================
# /analyze-with-ai ENDPOINT
# ================================

@app.post("/analyze-with-ai")
def analyze_with_ai(request: AnalysisRequest):

    if not request.issues:
        return {
            "analysis": "No vulnerabilities detected.",
            "secure_code": request.code,
            "explanation": "Your code appears secure.",
            "source": "openai"
        }

    if not LOCAL_AI_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="OpenAI Engine not available. No fix available from our end."
        )

    vulnerabilities = [
        Vulnerability(
            issue.get("type", "UNKNOWN"),
            issue.get("line", 1),
            issue.get("description", "Security issue")
        )
        for issue in request.issues
    ]

    try:
        explanation_response = generate_explanation(request.code, vulnerabilities)
        secure_code_response = generate_secure_code(request.code, vulnerabilities)

        if (
            not isinstance(secure_code_response, str) or
            not secure_code_response.strip() or
            secure_code_response.startswith("ERROR")
        ):
            raise HTTPException(
                status_code=500,
                detail="No fix available from our end. Invalid AI secure code output."
            )

        explanation_data = None
        if isinstance(explanation_response, str):
            try:
                explanation_data = json.loads(explanation_response)
            except json.JSONDecodeError:
                explanation_data = None
        elif isinstance(explanation_response, dict):
            explanation_data = explanation_response

        detailed_explanation = explanation_response
        if explanation_data and "vulnerabilities" in explanation_data:
            formatted = []
            for vuln in explanation_data["vulnerabilities"]:
                formatted.append(
                    f"### {vuln.get('type')} (Line {vuln.get('line')})\n"
                    f"Severity: {vuln.get('severity')}\n\n"
                    f"Cause: {vuln.get('cause')}\n"
                    f"Risk: {vuln.get('risk')}\n"
                    f"Fix: {vuln.get('fix')}\n\n---"
                )
            detailed_explanation = "\n".join(formatted)

        return {
            "analysis": explanation_response,
            "secure_code": secure_code_response,
            "explanation": detailed_explanation,
            "issues": request.issues,
            "source": "openai"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {str(e)}. No fix available from our end."
        )
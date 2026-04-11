from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess, json, uuid, os
from pathlib import Path
import sys

# Add AI Reasoning Engine to path
ai_engine_path = Path(__file__).resolve().parent.parent / "AI-Reasoning-Engine"
sys.path.insert(0, str(ai_engine_path))

# Define Vulnerability class locally (fallback)
class Vulnerability:
    def __init__(self, vuln_type: str, line: int, description: str):
        self.type = vuln_type
        self.line = line
        self.description = description
    
    def to_dict(self):
        return {
            "type": self.type,
            "line": self.line,
            "description": self.description
        }

# Try to import from AI engine
try:
    from ai_security_analyzer.app.reasoning import generate_explanation
    from ai_security_analyzer.app.secure_generator import generate_secure_code
    LOCAL_AI_AVAILABLE = True
    print("✓ Local AI Engine imported successfully")
except ImportError as e:
    print(f"⚠ Local AI Engine not available: {e}")
    LOCAL_AI_AVAILABLE = False

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str

class AnalysisRequest(BaseModel):
    code: str
    issues: list

@app.post("/analyze")
def analyze(data: CodeInput):

    code = data.code
    uid = str(uuid.uuid4())

    # project root = AurIx-main
    root = Path(__file__).resolve().parent.parent
    temp_dir = root / "temp_files"
    temp_dir.mkdir(exist_ok=True)

    temp_file = temp_dir / f"temp_{uid}.py"
    out_file = root / f"results/temp_{uid}.json"

    # save incoming code
    temp_file.write_text(code, encoding="utf-8")

    # run YOUR detect.py engine
    subprocess.run([
        "python",
        str(root / "detect.py"),
        str(temp_file),
        "--only-issues",
        "--compact",
        "-o",
        str(out_file)
    ], cwd=root)

    # if engine produced no file
    if not out_file.exists():
        return {"issues": []}

    data_json = json.loads(out_file.read_text(encoding="utf-8"))

    issues = []

    # Map vulnerability categories to severity levels
    severity_mapping = {
        "INJC": "high",      # Injection
        "IDAF": "high",      # Insecure Data Access
        "SDIF": "high",      # Secure Deserialization/Insecure Formats
        "CRYF": "high",      # Cryptography Failures
        "CRYP": "high",      # Cryptographic Issues
        "SECM": "medium",    # Security Misconfiguration
        "BRAC": "high",      # Broken Access Control
    }
    
    # Map vulnerability types to user-friendly names
    type_mapping = {
        "SQL": "SQL Injection",
        "SUBPROCESS": "Command Injection",
        "SUBPROC": "Command Injection",
        "CREDENTIALS": "Hard-coded Credentials",
        "PICKLE": "Insecure Deserialization",
        "EVAL": "Code Injection",
        "WITH-OPEN": "Path Traversal",
        "MD5": "Weak Cryptography",
        "ELEMENTTREE": "XXE (XML External Entity)",
        "RANDOM": "Weak Random Generation",
        "REQUEST": "Broken Access Control",
        "DEBUG": "Security Misconfiguration",
    }

    # convert detect.py output → extension format
    for file in data_json:
        for item in data_json[file]:
            # Fix the line number offset: detect.py reports 2*line - 1, so reverse it
            reported_line = item.get("line", 1)
            line = int((reported_line + 1) / 2)  # Convert back to actual line number
            
            categories = item.get("categories", [])
            rules = item.get("rules", [])
            code = item.get("code", "")
            
            # Get primary category for severity mapping
            primary_category = categories[0] if categories else "SECM"
            severity = severity_mapping.get(primary_category, "medium")
            
            # Build friendly type name from rules
            type_name = "Security Vulnerability"
            for rule in rules:
                for key, value in type_mapping.items():
                    if key in rule:
                        type_name = value
                        break
                if type_name != "Security Vulnerability":
                    break
            
            # Build detailed description
            categories_str = ", ".join(categories) if categories else "Security Issue"
            description = f"{categories_str} - Line contains: {code[:60]}..." if code else categories_str
            
            issues.append({
                "type": type_name,
                "description": description,
                "severity": severity,
                "line": line,
                "column": 1,
                "code": code,
                "rules": rules,
                "categories": categories
            })

    # cleanup temp files
    try:
        temp_file.unlink(missing_ok=True)
        out_file.unlink(missing_ok=True)
    except:
        pass

    print(f"AurIx Backend: Detected {len(issues)} vulnerabilities")
    return {"issues": issues}


@app.post("/analyze-with-ai")
def analyze_with_ai(request: AnalysisRequest):
    """
    Takes code + detected vulnerabilities and generates analysis using local AI model
    Falls back to template if Ollama not available
    """
    try:
        code = request.code
        issues = request.issues
        
        if not issues:
            return {
                "analysis": "No vulnerabilities detected in this code.",
                "secure_code": code,
                "explanation": "Your code appears to be secure!"
            }
        
        # Convert issues to Vulnerability objects
        vulnerabilities = []
        for issue in issues:
            vuln = Vulnerability(
                vuln_type=issue.get('type', 'UNKNOWN'),
                line=issue.get('line', 1),
                description=issue.get('description', 'Security issue detected')
            )
            vulnerabilities.append(vuln)
        
        print(f"AurIx: Processing {len(vulnerabilities)} vulnerabilities...")
        
        # Try to use local AI if available
        if LOCAL_AI_AVAILABLE:
            try:
                print(f"AurIx: Attempting to generate analysis with Ollama...")
                
                # Test Ollama connection
                import requests
                try:
                    requests.post(
                        "http://localhost:11434/api/generate",
                        json={"model": "qwen2.5:7b", "prompt": "test", "stream": False},
                        timeout=3
                    )
                    print("✓ Ollama connection successful")
                except requests.exceptions.ConnectionError:
                    print("✗ Ollama not running - using template response")
                    return generate_template_response(code, issues)
                except Exception as e:
                    print(f"✗ Ollama error: {e} - using template response")
                    return generate_template_response(code, issues)
                
                # Generate with AI
                print(f"AurIx: Generating explanation...")
                explanation_response = generate_explanation(code, vulnerabilities)
                
                print(f"AurIx: Generating secure code...")
                secure_code_response = generate_secure_code(code, vulnerabilities)
                
                # Parse explanation
                try:
                    explanation_data = json.loads(explanation_response)
                    analysis = json.dumps(explanation_data, indent=2)
                except:
                    analysis = explanation_response
                
                # Build detailed explanation
                detailed_explanation = ""
                if isinstance(explanation_data, dict) and "vulnerabilities" in explanation_data:
                    for vuln_item in explanation_data.get("vulnerabilities", []):
                        detailed_explanation += f"""
### {vuln_item.get('type', 'Vulnerability')} (Line {vuln_item.get('line', 1)})
**Severity:** {vuln_item.get('severity', 'Unknown')}

**Cause:** {vuln_item.get('cause', 'Security issue detected')}

**Security Risk:** {vuln_item.get('risk', 'This could compromise your application')}

**How to Fix:** {vuln_item.get('fix', 'Apply security best practices')}

---
"""
                
                print("✓ AI Analysis completed successfully")
                
                return {
                    "analysis": analysis,
                    "secure_code": secure_code_response,
                    "explanation": detailed_explanation if detailed_explanation else secure_code_response
                }
            
            except Exception as e:
                print(f"✗ Local AI error: {str(e)}")
                print("AurIx: Falling back to template analysis")
                return generate_template_response(code, issues)
        else:
            print("AurIx: Local AI Engine not available - using template response")
            return generate_template_response(code, issues)
    
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return generate_template_response(code, issues)


def generate_template_response(code, issues):
    """Fallback template-based analysis when AI API fails"""
    
    # Map vulnerability types to security explanations
    vuln_explanations = {
        "pickle.loads": {
            "risk": "Arbitrary Code Execution (ACE)",
            "why": "pickle.loads() can deserialize and execute arbitrary Python code embedded in untrusted data. An attacker can craft malicious pickle data to run any code on your system.",
            "impact": "Complete system compromise, data theft, ransomware installation",
            "fix": "Use json.loads() for safe deserialization, or implement strict validation",
            "secure": "obj = json.loads(user_data)"
        },
        "eval": {
            "risk": "Code Injection / Arbitrary Code Execution",
            "why": "eval() executes any string as Python code. If the string comes from user input, attackers can execute malicious code directly.",
            "impact": "Full application compromise, data theft, privilege escalation",
            "fix": "Use ast.literal_eval() for safe expression evaluation, or json.loads() for data",
            "secure": "obj = ast.literal_eval(user_input)  # Safe for literals only"
        },
        "shell=True": {
            "risk": "Command Injection",
            "why": "When shell=True, the command string is parsed by the shell, allowing shell metacharacters to be interpreted. User input in the command can inject additional commands.",
            "impact": "Remote code execution, system compromise, data exfiltration",
            "fix": "Always use shell=False and pass arguments as a list",
            "secure": "subprocess.run(['cat', filename], shell=False)"
        },
        "hardcoded": {
            "risk": "Credential Exposure",
            "why": "Hardcoded secrets in source code are visible to anyone with access to the codebase, including version control history. Can lead to unauthorized access.",
            "impact": "Account compromise, unauthorized API access, system breach",
            "fix": "Use environment variables, secrets manager, or .env files (not in git)",
            "secure": "api_key = os.getenv('API_KEY')"
        },
        "hashlib.md5": {
            "risk": "Weak Cryptography",
            "why": "MD5 is cryptographically broken. It can be cracked quickly with modern hardware, allowing attackers to forge credentials.",
            "impact": "Password cracking, authentication bypass, hash collision attacks",
            "fix": "Use bcrypt, scrypt, or Argon2 for passwords; SHA-256+ for hashing",
            "secure": "import bcrypt; hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())"
        },
        "random.randint": {
            "risk": "Weak Random Number Generation",
            "why": "random module is not cryptographically secure. Attackers can predict token values if they know the seed.",
            "impact": "Session hijacking, token prediction, security bypass",
            "fix": "Use secrets module or os.urandom() for security-related randomness",
            "secure": "import secrets; token = secrets.token_hex(16)"
        }
    }
    
    # Build analysis based on issues
    analysis_parts = []
    explanation_parts = []
    
    for issue in issues:
        issue_type = issue.get('type', '').lower()
        description = issue.get('description', '')
        line_num = issue.get('line', 1)
        
        # Find matching explanation
        matched = False
        for key, exp in vuln_explanations.items():
            if key.lower() in issue_type.lower() or key.lower() in description.lower() or key in code.lower():
                matched = True
                analysis_parts.append(f"**Line {line_num}: {issue_type}**\n{exp['why']}")
                explanation_parts.append(f"### {exp['risk']} (Line {line_num})\n\n**Why this is dangerous:**\n{exp['why']}\n\n**Potential Impact:**\n{exp['impact']}\n\n**How to fix:**\n{exp['fix']}\n\n**Secure Example:**\n```python\n{exp['secure']}\n```")
                break
        
        if not matched:
            analysis_parts.append(f"**Line {line_num}: {issue_type}**\n{description}\n\n**Security Risk:** This vulnerability could allow attackers to compromise your application. Review the code and apply proper security controls.")
            explanation_parts.append(f"### {issue_type} (Line {line_num})\n\n**Issue:** {description}\n\n**Recommendation:** Validate and sanitize all user input, use safe APIs, and apply principle of least privilege.")
    
    # Generate improved secure code - scan code directly for patterns
    improved_code = code
    secure_code_replacements = []
    
    # Define search patterns and replacements
    replacements = [
        # Pickle deserialization
        {
            "patterns": ["pickle.loads", "pickle.load"],
            "search": "pickle.loads",
            "replace": "json.loads",
            "import_add": "import json",
            "import_remove": "import pickle",
            "message": "✓ Replaced pickle with json for safe deserialization"
        },
        # Eval usage
        {
            "patterns": ["eval("],
            "search": "eval(",
            "replace": "ast.literal_eval(",
            "import_add": "import ast",
            "import_remove": None,
            "message": "✓ Replaced eval() with ast.literal_eval() for safe evaluation"
        },
        # Command injection
        {
            "patterns": ["shell=True"],
            "search": "shell=True",
            "replace": "shell=False",
            "import_add": None,
            "import_remove": None,
            "message": "✓ Changed shell=True to shell=False to prevent command injection"
        },
        # MD5 weak crypto
        {
            "patterns": ["hashlib.md5"],
            "search": "hashlib.md5",
            "replace": "hashlib.sha256",
            "import_add": None,
            "import_remove": None,
            "message": "✓ Upgraded md5 to sha256"
        },
        # Random for security
        {
            "patterns": ["random.randint", "random.random()", "random.choice"],
            "search": "import random",
            "replace": "import secrets",
            "import_add": "import secrets",
            "import_remove": None,
            "message": "✓ Replaced random with secrets module for cryptographic randomness"
        }
    ]
    
    # Apply replacements by scanning code
    for replacement in replacements:
        patterns_found = False
        for pattern in replacement.get("patterns", []):
            if pattern in improved_code:
                patterns_found = True
                break
        
        if patterns_found:
            # Apply replacement
            improved_code = improved_code.replace(replacement["search"], replacement["replace"])
            
            # Handle imports
            if replacement.get("import_add"):
                if replacement["import_add"] not in improved_code:
                    improved_code = replacement["import_add"] + "\n" + improved_code
            
            if replacement.get("import_remove"):
                improved_code = improved_code.replace(replacement["import_remove"] + "\n", "")
                improved_code = improved_code.replace(replacement["import_remove"], "")
            
            secure_code_replacements.append(replacement["message"])
    
    # Additional hardcoded credentials scanning and replacement
    lines = improved_code.split('\n')
    new_lines = []
    has_hardcoded_creds = False
    
    for line in lines:
        # Look for patterns like: api_key = "...", password = "...", etc.
        is_credentials_line = ('api_key' in line.lower() or 'password' in line.lower() or 
                               'secret' in line.lower() or 'token' in line.lower())
        
        if is_credentials_line and '=' in line and '"' in line:
            # Extract variable name and check if value looks hardcoded
            try:
                parts = line.split('=')
                if len(parts) >= 2:
                    var_part = parts[0].strip()
                    value_part = '='.join(parts[1:]).strip()
                    
                    # Check if it's a string literal with quotes
                    if value_part.startswith('"') or value_part.startswith("'"):
                        # Convert to environment variable access
                        line = f'{var_part} = os.getenv("{var_part.upper()}")'
                        has_hardcoded_creds = True
            except:
                pass
        
        new_lines.append(line)
    
    improved_code = '\n'.join(new_lines)
    
    if has_hardcoded_creds:
        if 'import os' not in improved_code:
            improved_code = 'import os\n' + improved_code
        secure_code_replacements.append("✓ Moved hardcoded credentials to environment variables")
    
    # Remove duplicates from replacements list
    secure_code_replacements = list(dict.fromkeys(secure_code_replacements))
    
    fix_summary = "\n".join(secure_code_replacements) if secure_code_replacements else "✓ Code has been analyzed for security best practices"
    
    # Return a dict, not json.dumps() - let FastAPI handle serialization
    return {
        "analysis": "\n\n".join(analysis_parts) if analysis_parts else "Code analyzed. No immediate security issues detected.",
        "secure_code": improved_code,
        "explanation": f"## Security Fixes Applied\n\n{fix_summary}\n\n## Detailed Explanation\n\n" + "\n\n".join(explanation_parts) if explanation_parts else "Review the secure code implementation above for security best practices."
    }
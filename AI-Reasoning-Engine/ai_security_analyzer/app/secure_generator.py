import json
from app.llm_client import call_llm
from app.config import Config
from app.models import serialize_vulnerabilities


def generate_secure_code(code_snippet, vulnerabilities):
    vuln_data = serialize_vulnerabilities(vulnerabilities)

    prompt = f"""
You are a secure coding expert.

Fix the code by removing vulnerabilities.

CODE:
{code_snippet}

ISSUES:
{json.dumps(vuln_data, indent=2)}

Requirements:
- Return ONLY fixed code
- Keep functionality same
- Use best practices
- Add brief comments explaining fixes
- Do NOT include explanations outside code
"""

    return call_llm(prompt, Config.TEMPERATURE_CODE)
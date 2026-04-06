import json
from app.llm_client import call_llm
from app.config import Config
from app.models import serialize_vulnerabilities


def generate_explanation(code_snippet, vulnerabilities):
    vuln_data = serialize_vulnerabilities(vulnerabilities)

    prompt = f"""
You are a cybersecurity expert.

Analyze the code and vulnerabilities.

CODE:
{code_snippet}

VULNERABILITIES:
{json.dumps(vuln_data, indent=2)}

Return STRICT JSON in this format:

{{
  "vulnerabilities": [
    {{
      "type": "...",
      "line": ...,
      "cause": "...",
      "risk": "...",
      "fix": "...",
      "severity": "Low | Medium | High | Critical"
    }}
  ]
}}

Rules:
- Be clear and beginner-friendly
- Do NOT add extra text outside JSON
"""

    return call_llm(prompt, Config.TEMPERATURE_REASONING)
from .gemini_client import ask_gemini


def generate_explanation(code: str, vulnerabilities: list) -> str:
    vuln_text = "\n".join(
        [
            f"- {v.type} at line {v.line}: {v.description}"
            for v in vulnerabilities
        ]
    )

    prompt = f"""
You are a senior application security engineer.

Analyze the following vulnerable code and detected issues.

CODE:
{code}

DETECTED VULNERABILITIES:
{vuln_text}

Explain in clear human-friendly language:
1. Root cause
2. Security risk
3. Real-world attack impact
4. Best secure fix
5. Severity level
"""

    return ask_gemini(prompt)
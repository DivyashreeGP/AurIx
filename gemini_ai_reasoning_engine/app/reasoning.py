from .openai_client import ask_openai


def generate_explanation(code: str, vulnerabilities: list) -> str:

    vuln_text = "\n".join(
        [
            f"- {v.type} at line {v.line}: {v.description}"
            for v in vulnerabilities
        ]
    )

    prompt = f"""
You are a senior application security engineer and vulnerability analysis expert.

Analyze the following vulnerable code and detected issues.

CODE:
{code}

DETECTED VULNERABILITIES:
{vuln_text}

For EACH vulnerability generate the explanation separately in the following EXACT format:

# [Vulnerability Name] (Line [line number])

## Why it is detected
Explain clearly why this vulnerability is detected in the code.

## What it can do
Explain what attackers can do using this vulnerability.

## Effect of not fixing
Explain the security impact and real-world consequences if not fixed.

## How to fix
Explain the proper secure remediation method.

## Example fix line
Provide a secure corrected code line or short secure code snippet inside a python code block.

--------------------------------------------------

IMPORTANT RULES:
- Generate separate sections for every vulnerability.
- Do NOT combine vulnerabilities together.
- Use simple human-friendly language.
- Keep explanations concise and readable.
- Use proper markdown headings.
- Always include the detected line number in heading.
- Always include code block for fix example.
- Do NOT generate extra sections.
- Explanations must match the actual vulnerability type.

Now generate the final vulnerability report.
"""

    return ask_openai(prompt)
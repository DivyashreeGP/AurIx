from app.reasoning import generate_explanation
from app.secure_generator import generate_secure_code
from app.models import Vulnerability


def run_demo():
    # 🔥 Example code with MULTIPLE vulnerabilities
    code = """
import os

password = "admin123"  # hardcoded secret

user_input = input("Enter username: ")

query = "SELECT * FROM users WHERE username = '" + user_input + "'"  # SQL injection

eval("print('Hello')")  # unsafe eval
"""

    vulnerabilities = [
        Vulnerability(
            vuln_type="SQL Injection",
            line=7,
            description="User input concatenated into SQL query"
        ),
        Vulnerability(
            vuln_type="Hardcoded Credential",
            line=3,
            description="Hardcoded password detected"
        ),
        Vulnerability(
            vuln_type="Code Injection",
            line=9,
            description="Use of eval() is unsafe"
        )
    ]

    print("\n==============================")
    print("🚨 INPUT CODE")
    print("==============================")
    print(code)

    print("\n==============================")
    print("🧠 AI EXPLANATION")
    print("==============================")
    explanation = generate_explanation(code, vulnerabilities)
    print(explanation)

    print("\n==============================")
    print("🔐 SECURE CODE")
    print("==============================")
    secure_code = generate_secure_code(code, vulnerabilities)
    print(secure_code)


if __name__ == "__main__":
    run_demo()
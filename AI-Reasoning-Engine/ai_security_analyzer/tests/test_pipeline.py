from app.reasoning import generate_explanation
from app.secure_generator import generate_secure_code
from app.models import Vulnerability


def run_test():
    code = """
query = "SELECT * FROM users WHERE username = '" + user_input + "'"
"""

    vulnerabilities = [
        Vulnerability(
            vuln_type="SQL Injection",
            line=1,
            description="User input directly concatenated into SQL query"
        )
    ]

    print("\n=== INPUT CODE ===")
    print(code)

    print("\n=== AI EXPLANATION ===")
    explanation = generate_explanation(code, vulnerabilities)
    print(explanation)

    print("\n=== SECURE CODE ===")
    secure_code = generate_secure_code(code, vulnerabilities)
    print(secure_code)


if __name__ == "__main__":
    run_test()
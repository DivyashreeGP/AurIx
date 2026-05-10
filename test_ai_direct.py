#!/usr/bin/env python
"""Test AI engine directly without HTTP"""
import sys
from pathlib import Path

# Setup path like main.py does
ai_engine_path = Path(__file__).resolve().parent / "gemini_ai_reasoning_engine"
sys.path.insert(0, str(ai_engine_path))

# Try to import AI functions
try:
    from gemini_ai_reasoning_engine.app.reasoning import generate_explanation
    from gemini_ai_reasoning_engine.app.secure_generator import generate_secure_code
    print("✓ AI Engine imports successful")
except Exception as e:
    print(f"✗ AI Engine import failed: {e}")
    sys.exit(1)

# Test with sample code
code = "import os\nos.system('ls -la')\n"

class Vuln:
    def __init__(self):
        self.type = "OS-SYSTEM-002"
        self.line = 2
        self.description = "os.system() call"

vulns = [Vuln()]

# Try to generate explanation
try:
    print("\nGenerating explanation...")
    explanation = generate_explanation(code, vulns)
    print("✓ Explanation generated:")
    print(explanation[:300])
except Exception as e:
    print(f"✗ Explanation failed: {e}")

# Try to generate secure code
try:
    print("\nGenerating secure code...")
    secure = generate_secure_code(code, vulns)
    print("✓ Secure code generated:")
    print(secure[:300])
except Exception as e:
    print(f"✗ Secure code failed: {e}")

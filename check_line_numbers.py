#!/usr/bin/env python3
"""Check what detect.py is reporting for line numbers"""
import json
import subprocess
from pathlib import Path

code = """import pickle
data = request.args.get('x')
obj = pickle.loads(data)"""

# Save to temp file
test_file = Path('temp_test_lines.py')
test_file.write_text(code)

# Run detect.py
subprocess.run(['python', 'detect.py', str(test_file), '--only-issues', '--compact', '-o', 'temp_output.json'])

# Read output
output = json.loads(Path('temp_output.json').read_text())
print("Raw detect.py output:")
print(json.dumps(output, indent=2))

# Clean up
test_file.unlink()
Path('temp_output.json').unlink()

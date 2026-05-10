# Secure code examples that should NOT be flagged as vulnerable

# 1. Parameterized SQL query (secure)
def get_user_by_id(user_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# 2. Input validation (secure)
def process_input(user_input):
    validated = int(user_input)  # Explicitly converted to int
    return validated * 2

# 3. HTML escaping (secure)
from html import escape
def safe_render(user_data):
    return escape(user_data)

# 4. Secure password handling
from werkzeug.security import generate_password_hash, check_password_hash
def hash_password(password):
    return generate_password_hash(password)

# 5. Safe file path validation
import os
def get_safe_file(path):
    if os.path.isfile(path):
        with open(path) as f:
            return f.read()

# 6. URL validation
from urllib.parse import urlparse
def validate_url(url):
    parsed = urlparse(url)
    if parsed.scheme in {'http', 'https'}:
        return parsed.netloc

# 7. Secure subprocess
import subprocess
def run_command(cmd):
    result = subprocess.run(cmd, shell=False, capture_output=True)
    return result.stdout
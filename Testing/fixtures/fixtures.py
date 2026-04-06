"""Test fixtures - Vulnerable code samples for testing"""

VULNERABLE_SQL = """
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect(':memory:')
    # VULNERABLE: SQL Injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor = conn.execute(query)
    return cursor.fetchone()
"""

VULNERABLE_PICKLE = """
import pickle

def load_data(data):
    # VULNERABLE: Unsafe deserialization
    obj = pickle.loads(data)
    return obj
"""

VULNERABLE_EVAL = """
def calculate(expression):
    # VULNERABLE: Arbitrary code execution
    result = eval(expression)
    return result
"""

VULNERABLE_OS_COMMAND = """
import os

def list_files(directory):
    # VULNERABLE: Command injection
    os.system(f'ls {directory}')
"""

VULNERABLE_HARDCODED = """
# VULNERABLE: Hardcoded credentials
DATABASE_PASSWORD = 'admin123'
API_KEY = 'sk-1234567890abcdefghijklmnop'
AWS_SECRET = 'aws_secret_access_key_value_here'
"""

VULNERABLE_WEAK_HASH = """
import hashlib

def hash_password(password):
    # VULNERABLE: MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()
"""

VULNERABLE_RANDOM = """
import random

def generate_token():
    # VULNERABLE: Weak random generation
    token = random.randint(100000, 999999)
    return str(token)
"""

VULNERABLE_XXE = """
import xml.etree.ElementTree as ET

def parse_xml(xml_string):
    # VULNERABLE: XXE attack
    root = ET.fromstring(xml_string)
    return root
"""

VULNERABLE_PATH_TRAVERSAL = """
def read_file(user_path):
    # VULNERABLE: Path traversal
    with open(user_path, 'r') as f:
        return f.read()
"""

VULNERABLE_UNVALIDATED_REDIRECT = """
from flask import Flask, redirect, request

app = Flask(__name__)

@app.route('/redirect')
def do_redirect():
    # VULNERABLE: Unvalidated redirect
    url = request.args.get('url')
    return redirect(url)
"""

VULNERABLE_NO_RATE_LIMIT = """
from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    # VULNERABLE: No rate limiting
    username = request.form['username']
    password = request.form['password']
    # Check credentials
    return 'Login successful'
"""

VULNERABLE_CORS = """
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
# VULNERABLE: CORS allows all origins
CORS(app, resources={r"/*": {"origins": "*"}})
"""

VULNERABLE_CSRF = """
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/transfer', methods=['POST'])
def transfer_money():
    # VULNERABLE: No CSRF token validation
    amount = request.form['amount']
    # Transfer money
    return 'Transfer complete'
"""

SECURE_JSON = """
import json

def load_data(data):
    # SECURE: JSON is safe for deserialization
    obj = json.loads(data)
    return obj
"""

SECURE_SQL = """
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect(':memory:')
    # SECURE: Parameterized query
    cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()
"""

SECURE_SUBPROCESS = """
import subprocess

def list_files(directory):
    # SECURE: Using subprocess with shell=False
    result = subprocess.run(['ls', directory], capture_output=True, shell=False)
    return result.stdout.decode()
"""

SECURE_HASH = """
import bcrypt

def hash_password(password):
    # SECURE: Using bcrypt for password hashing
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()
"""

SECURE_SECRETS = """
import os
from dotenv import load_dotenv

load_dotenv()

# SECURE: Using environment variables
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
API_KEY = os.getenv('API_KEY')
"""

# Export all samples
VULNERABLE_SAMPLES = [
    ("SQL Injection", VULNERABLE_SQL),
    ("Pickle Deserialization", VULNERABLE_PICKLE),
    ("Eval Execution", VULNERABLE_EVAL),
    ("OS Command Injection", VULNERABLE_OS_COMMAND),
    ("Hardcoded Credentials", VULNERABLE_HARDCODED),
    ("Weak Hashing", VULNERABLE_WEAK_HASH),
    ("Weak Random", VULNERABLE_RANDOM),
    ("XXE Attack", VULNERABLE_XXE),
    ("Path Traversal", VULNERABLE_PATH_TRAVERSAL),
    ("Unvalidated Redirect", VULNERABLE_UNVALIDATED_REDIRECT),
    ("No Rate Limiting", VULNERABLE_NO_RATE_LIMIT),
    ("CORS Misconfiguration", VULNERABLE_CORS),
    ("CSRF Missing Token", VULNERABLE_CSRF),
]

SECURE_SAMPLES = [
    ("JSON Deserialization", SECURE_JSON),
    ("Parameterized SQL", SECURE_SQL),
    ("Subprocess Safe", SECURE_SUBPROCESS),
    ("Secure Hashing", SECURE_HASH),
    ("Environment Variables", SECURE_SECRETS),
]

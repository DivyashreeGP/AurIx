"""
secure_code_generator.py
Backend service to generate secure code examples for vulnerabilities
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

# ===== DATA MODELS =====

class VulnerabilityType(str, Enum):
    SQL_INJECTION = "SQL Injection"
    PICKLE_VULNERABILITY = "Pickle Vulnerability"
    EVAL_USAGE = "Eval Usage"
    HARDCODED_CREDENTIALS = "Hardcoded Credentials"
    WEAK_CRYPTOGRAPHY = "Weak Cryptography"
    DEBUG_MODE = "Debug Mode Enabled"


@dataclass
class CodeExample:
    title: str
    method: str
    code: str
    language: str = "python"


@dataclass
class SecureCodeSuggestion:
    vulnerability_type: VulnerabilityType
    original_line: str
    original_code: str
    explanation: str
    risk: str
    how_to_fix: List[str]
    secure_code_examples: List[CodeExample]
    no_code_message: Optional[str] = None


# ===== SECURE CODE EXAMPLES DATABASE =====

SECURE_CODE_LIBRARY = {
    VulnerabilityType.SQL_INJECTION: {
        "explanation": "Direct string concatenation with user input allows SQL injection attacks",
        "risk": "Attacker can bypass query logic, extract/modify data, or execute arbitrary SQL",
        "how_to_fix": [
            "Use parameterized queries (prepared statements)",
            "Never concatenate user input into SQL directly",
            "Validate and sanitize input types and lengths",
            "Use ORM frameworks (SQLAlchemy, Django ORM)",
            "Apply principle of least privilege to database users",
            "Implement query result length limits"
        ],
        "examples": [
            CodeExample(
                title="Method 1: Parameterized Query (sqlite3)",
                method="Using ? placeholders with execute()",
                code="""cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
result = cursor.fetchone()"""
            ),
            CodeExample(
                title="Method 2: Named Parameters (PostgreSQL)",
                method="Using named placeholders for clarity",
                code="""cursor.execute(
    "SELECT * FROM users WHERE id=%(user_id)s AND email=%(email)s",
    {"user_id": user_id, "email": user_email}
)
result = cursor.fetchone()"""
            ),
            CodeExample(
                title="Method 3: SQLAlchemy ORM",
                method="Object-relational mapping with automatic parameterization",
                code="""from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

with Session(engine) as session:
    user = session.query(User).filter(User.id == user_id).first()
    
# Or using newer syntax:
stmt = select(User).where(User.id == user_id)
user = session.scalars(stmt).first()"""
            ),
            CodeExample(
                title="Method 4: Django ORM",
                method="Django's built-in protection",
                code="""try:
    user = User.objects.get(id=user_id)
except User.DoesNotExist:
    user = None

# Or filter:
users = User.objects.filter(id=user_id, status='active')"""
            ),
        ]
    },
    
    VulnerabilityType.PICKLE_VULNERABILITY: {
        "explanation": "pickle.loads() on untrusted data can lead to arbitrary code execution",
        "risk": "Attacker can execute arbitrary code by crafting malicious pickle payloads",
        "how_to_fix": [
            "NEVER pickle untrusted data",
            "Prefer JSON/MessagePack for external data serialization",
            "If pickle is necessary, use RestrictedUnpickler",
            "Validate file origins and signatures before deserialization",
            "Keep Python and libraries updated for security patches",
            "Implement file integrity checks (HMAC/signatures)"
        ],
        "examples": [
            CodeExample(
                title="Method 1: Use JSON Instead (SAFEST)",
                method="JSON is safe and language-independent",
                code="""import json

# Serialize
data = {"user": "john", "id": 123}
serialized = json.dumps(data)

# Deserialize
data = json.loads(serialized)"""
            ),
            CodeExample(
                title="Method 2: Use ast.literal_eval",
                method="Safe evaluation for Python literals only",
                code="""import ast

data_string = "{'key': 'value', 'numbers': [1, 2, 3]}"
try:
    data = ast.literal_eval(data_string)
except (ValueError, SyntaxError) as e:
    print(f"Invalid data: {e}")
    data = None"""
            ),
            CodeExample(
                title="Method 3: Restricted Pickle with Whitelist",
                method="If you must use pickle, validate class types",
                code="""import pickle
from io import BytesIO

class RestrictedUnpickler(pickle.Unpickler):
    ALLOWED_CLASSES = {'User', 'Product', 'Order'}
    
    def find_class(self, module, name):
        if module == "myapp.models" and name in self.ALLOWED_CLASSES:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"Unsafe: {module}.{name}")

# Use it:
data = RestrictedUnpickler(BytesIO(pickled_data)).load()"""
            ),
            CodeExample(
                title="Method 4: MessagePack (Alternative)",
                method="Safer than pickle, preserves types",
                code="""import msgpack

# Serialize
data = {"user": "john", "age": 30}
packed = msgpack.packb(data)

# Deserialize
unpacked = msgpack.unpackb(packed, raw=False)"""
            ),
        ]
    },
    
    VulnerabilityType.EVAL_USAGE: {
        "explanation": "eval() executes arbitrary Python code from strings",
        "risk": "Attacker can execute malicious code with full Python capabilities",
        "how_to_fix": [
            "NEVER use eval() on user input",
            "Use ast.literal_eval() for Python literals",
            "Use restricted evaluation libraries",
            "Implement whitelisting for allowed operations",
            "Create sandboxed environments if dynamic code is needed"
        ],
        "examples": [
            CodeExample(
                title="Method 1: ast.literal_eval (For Literals)",
                method="Safe evaluation of Python data structures",
                code="""import ast

user_input = "{'name': 'John', 'age': 30}"
try:
    data = ast.literal_eval(user_input)
except (ValueError, SyntaxError):
    data = None"""
            ),
            CodeExample(
                title="Method 2: Custom Expression Parser",
                method="Parse specific, safe expressions",
                code="""import re
from operator import add, sub, mul, truediv

def safe_calc(expression):
    # Only allow numbers and specific operators
    if not re.match(r'^[0-9+\\-*/().\\s]+$', expression):
        raise ValueError("Invalid expression")
    
    # Use operator module instead of eval
    return eval(expression, {"__builtins__": {}}, {})

result = safe_calc("10 + 5 * 2")"""
            ),
            CodeExample(
                title="Method 3: NumExpr for Math",
                method="Safe mathematical expression evaluation",
                code="""import numexpr
import numpy as np

array1 = np.array([1, 2, 3, 4, 5])
array2 = np.array([5, 4, 3, 2, 1])

# Safe expression evaluation
result = numexpr.evaluate('array1 + array2 * 2')"""
            ),
            CodeExample(
                title="Method 4: Restricted Code Environment",
                method="If dynamic code is absolutely needed",
                code="""import types

def safe_eval_expression(code, allowed_vars):
    # Create restricted environment
    safe_dict = {k: v for k, v in allowed_vars.items() if not k.startswith('_')}
    
    try:
        result = eval(code, {"__builtins__": {}}, safe_dict)
        return result
    except Exception as e:
        return None

# Use it:
allowed = {'x': 10, 'y': 20}
result = safe_eval_expression('x + y', allowed)"""
            ),
        ]
    },
    
    VulnerabilityType.HARDCODED_CREDENTIALS: {
        "explanation": "Credentials in source code can be extracted from repositories, binaries",
        "risk": "Exposed credentials allow attackers direct access to systems/services",
        "how_to_fix": [
            "Use environment variables for secrets",
            "Use secret management services (AWS Secrets Manager, HashiCorp Vault)",
            "Rotate credentials regularly",
            "Use IAM roles instead of credentials when possible",
            "Enable audit logging for credential access",
            "Never commit secrets to git (even in history)"
        ],
        "examples": [
            CodeExample(
                title="Method 1: Environment Variables",
                method="Simple approach using .env files",
                code="""import os
from dotenv import load_dotenv

load_dotenv()  # Loads from .env file (add to .gitignore!)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
API_KEY = os.getenv("API_KEY")

# Connect using variables
import psycopg2
conn = psycopg2.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database="myapp"
)"""
            ),
            CodeExample(
                title="Method 2: AWS Secrets Manager",
                method="AWS-native secure storage",
                code="""import boto3
import json

secrets_client = boto3.client('secretsmanager', region_name='us-east-1')

try:
    response = secrets_client.get_secret_value(SecretId='prod/db/password')
    
    if 'SecretString' in response:
        secret = json.loads(response['SecretString'])
        db_password = secret['password']
    
    import psycopg2
    conn = psycopg2.connect(
        host=secret['host'],
        user=secret['username'],
        password=db_password,
        database=secret['dbname']
    )
except Exception as e:
    print(f"Error retrieving secret: {e}")"""
            ),
            CodeExample(
                title="Method 3: HashiCorp Vault",
                method="Centralized secret management",
                code="""import hvac

# Initialize Vault client
client = hvac.Client(
    url='http://127.0.0.1:8200',
    token='s.XXXXXXXXXXXXXXXX'
)

# Read secret
secret_response = client.secrets.kv.v2.read_secret_version(
    path='database/credentials'
)

db_creds = secret_response['data']['data']
password = db_creds['password']"""
            ),
            CodeExample(
                title="Method 4: Python Keyring",
                method="OS-level credential storage",
                code="""import keyring

# Store credential (usually done once)
keyring.set_password("myapp", "db_user", "actual_password")

# Retrieve credential
password = keyring.get_password("myapp", "db_user")

# Or get from environment as fallback
import os
password = password or os.getenv("DB_PASSWORD")"""
            ),
        ]
    },
    
    VulnerabilityType.WEAK_CRYPTOGRAPHY: {
        "explanation": "MD5 and SHA1 are cryptographically broken and can be reversed",
        "risk": "Passwords hashed with MD5/SHA1 can be cracked in seconds using rainbow tables",
        "how_to_fix": [
            "Use bcrypt or Argon2 for passwords (NEVER MD5/SHA1)",
            "Use sha256+ for non-password hashing",
            "Add random salt (bcrypt/Argon2 do this automatically)",
            "Use high iteration counts (bcrypt default: 12 rounds)",
            "Never reuse salts across users",
            "Keep cryptography libraries updated"
        ],
        "examples": [
            CodeExample(
                title="Method 1: bcrypt (RECOMMENDED)",
                method="Industry standard for password hashing",
                code="""import bcrypt

# Hash password
password = "user_password_123"
salt = bcrypt.gensalt(rounds=12)
hashed_password = bcrypt.hashpw(password.encode(), salt)

# Store hashed_password in database

# Later, verify password
if bcrypt.checkpw(password.encode(), stored_hash):
    print("Password is correct!")
else:
    print("Password is incorrect")"""
            ),
            CodeExample(
                title="Method 2: Argon2 (Modern)",
                method="More secure than bcrypt, resistant to ASIC attacks",
                code="""from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

# Hash password
password = "user_password_123"
hashed = ph.hash(password)

# Store hashed in database

# Later, verify
try:
    ph.verify(hashed, password)
    print("Password correct!")
except VerifyMismatchError:
    print("Password incorrect")"""
            ),
            CodeExample(
                title="Method 3: PBKDF2 (Standard Library)",
                method="Part of Python's hashlib, no external deps",
                code="""import hashlib
import secrets

# Hash password
password = "user_password_123"
salt = secrets.token_bytes(32)

# Use PBKDF2 with 100,000+ iterations
password_hash = hashlib.pbkdf2_hmac(
    'sha256',
    password.encode(),
    salt,
    iterations=100000
)

# Store as: salt + hash
stored = salt + password_hash

# Later, verify
stored_salt = stored[:32]
stored_hash = stored[32:]
hash_attempt = hashlib.pbkdf2_hmac('sha256', password.encode(), stored_salt, 100000)
if hash_attempt == stored_hash:
    print("Password correct!")"""
            ),
            CodeExample(
                title="Method 4: Flask-Security Integration",
                method="Framework-level password handling",
                code="""from flask_security import Security, SQLAlchemyUserDatastore, hash_password

# Setup
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Hash password on registration
def register_user(email, password):
    user = User(
        email=email,
        password=hash_password(password),  # Automatically uses best algo
        active=True
    )
    db.session.add(user)
    db.session.commit()"""
            ),
        ]
    },
    
    VulnerabilityType.DEBUG_MODE: {
        "explanation": "Debug mode exposes stack traces, variable values, and application internals",
        "risk": "Attackers see exact error locations, library versions, and sometimes credentials in traces",
        "how_to_fix": [
            "Always disable debug in production",
            "Use environment variables to control debug state",
            "Implement proper error logging to secure location",
            "Use error tracking services (Sentry, DataDog)",
            "Set up centralized logging (ELK, CloudWatch)",
            "Monitor error logs for attack patterns"
        ],
        "examples": [
            CodeExample(
                title="Method 1: Flask Configuration",
                method="Environment-based debug setting",
                code="""import os
from flask import Flask

app = Flask(__name__)

# DEBUG based on environment
DEBUG_MODE = os.getenv('DEBUG', 'False') == 'True'
app.config['DEBUG'] = DEBUG_MODE

# Or explicitly:
if os.getenv('ENVIRONMENT') == 'development':
    app.run(debug=True, host='localhost')
else:
    app.run(debug=False)"""
            ),
            CodeExample(
                title="Method 2: Django Settings",
                method="Separate settings for dev/prod",
                code="""# settings.py
import os

DEBUG = os.getenv('DEBUG', 'False') == 'True'

if not DEBUG:
    ALLOWED_HOSTS = ['yourdomain.com']
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

# Use different settings files:
# from settings_prod import * for production"""
            ),
            CodeExample(
                title="Method 3: Error Handler with Logging",
                method="Custom error handling in production",
                code="""from flask import Flask, jsonify
import logging

app = Flask(__name__)

@app.errorhandler(Exception)
def handle_error(error):
    # Log full error internally
    app.logger.error(f"Unhandled error: {error}", exc_info=True)
    
    # Return generic response to user
    if app.config.get('DEBUG'):
        return jsonify({"error": str(error)}), 500
    else:
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": "Not found"}), 404"""
            ),
            CodeExample(
                title="Method 4: Error Tracking Service",
                method="Professional error monitoring with Sentry",
                code="""import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://key@sentry.io/12345",
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)

# Errors automatically captured and reported
from flask import Flask
app = Flask(__name__)

@app.route('/test')
def test_sentry():
    try:
        1 / 0
    except Exception as e:
        sentry_sdk.capture_exception(e)  # Manual reporting
        return {"error": "Something went wrong"}, 500"""
            ),
        ]
    }
}


# ===== GENERATOR FUNCTION =====

def generate_secure_code(vulnerability_type: VulnerabilityType, 
                        original_code: str) -> SecureCodeSuggestion:
    """
    Generate secure code suggestions for a given vulnerability
    
    Args:
        vulnerability_type: Type of vulnerability found
        original_code: The vulnerable code snippet
        
    Returns:
        SecureCodeSuggestion with examples and guidance
    """
    
    if vulnerability_type not in SECURE_CODE_LIBRARY:
        return SecureCodeSuggestion(
            vulnerability_type=vulnerability_type,
            original_line="",
            original_code=original_code,
            explanation="Unknown vulnerability type",
            risk="Unable to generate guidance",
            how_to_fix=["Consult with your security team"],
            secure_code_examples=[],
            no_code_message="No automated guidance available for this vulnerability type."
        )
    
    lib_entry = SECURE_CODE_LIBRARY[vulnerability_type]
    
    return SecureCodeSuggestion(
        vulnerability_type=vulnerability_type,
        original_line="",
        original_code=original_code,
        explanation=lib_entry["explanation"],
        risk=lib_entry["risk"],
        how_to_fix=lib_entry["how_to_fix"],
        secure_code_examples=lib_entry["examples"],
        no_code_message=None
    )


def generate_bulk_secure_code(vulnerabilities: List[Dict]) -> List[SecureCodeSuggestion]:
    """
    Generate secure code suggestions for multiple vulnerabilities
    """
    suggestions = []
    for vuln in vulnerabilities:
        try:
            vuln_type = VulnerabilityType(vuln.get('type'))
            suggestion = generate_secure_code(vuln_type, vuln.get('code', ''))
            suggestions.append(suggestion)
        except (ValueError, KeyError) as e:
            print(f"Error processing vulnerability: {e}")
            continue
    
    return suggestions


# ===== EXAMPLE USAGE =====

if __name__ == "__main__":
    # Example: SQL Injection
    vulnerable_sql = "query = 'SELECT * FROM users WHERE id=' + user_input"
    suggestion = generate_secure_code(VulnerabilityType.SQL_INJECTION, vulnerable_sql)
    
    print(f"Vulnerability: {suggestion.vulnerability_type}")
    print(f"Explanation: {suggestion.explanation}")
    print(f"Risk: {suggestion.risk}")
    print("\nHow to fix:")
    for i, step in enumerate(suggestion.how_to_fix, 1):
        print(f"  {i}. {step}")
    print("\nSecure Code Examples:")
    for example in suggestion.secure_code_examples:
        print(f"  - {example.title}")
        print(f"    Method: {example.method}")

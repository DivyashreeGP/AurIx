# Security Vulnerability UI - Reference & Secure Code Guide

## UI Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ VULNERABILITY DETAIL VIEW                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ⓘ SECURITY DISCLAIMER (Info Icon with Tooltip)                │
│   Hover: "Generated secure code is a guide. Security depends   │
│   on context, input validation, and architecture."            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ ORIGINAL CODE (Read-Only)                                       │
├─────────────────────────────────────────────────────────────────┤
│ Line 45:                                                        │
│   query = "SELECT * FROM users WHERE id=" + user_input        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ HOW TO FIX                                                      │
├─────────────────────────────────────────────────────────────────┤
│ 1. Use parameterized queries (prepared statements)             │
│ 2. Never concatenate user input into SQL directly              │
│ 3. Validate and sanitize input lengths                         │
│ 4. Use ORM frameworks when possible                            │
│ 5. Apply principle of least privilege to DB user               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ VULNERABILITY ANALYSIS                                          │
├─────────────────────────────────────────────────────────────────┤
│ • Type: SQL Injection                                          │
│ • Severity: HIGH                                               │
│ • Issue: Direct string concatenation with user input           │
│ • Risk: Attacker can bypass query logic, extract data          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ SECURE CODE REFERENCE                                          │
│ ⓘ This is a guide. Test thoroughly in your context.           │
├─────────────────────────────────────────────────────────────────┤
│ # Method 1: Using Parameterized Query (sqlite3)              │
│ cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))  │
│                                                                 │
│ # Method 2: Using ORM (SQLAlchemy)                            │
│ user = db.session.query(User).filter_by(id=user_id).first()   │
│                                                                 │
│ # Method 3: Using Django ORM                                   │
│ user = User.objects.get(id=user_id)                           │
│                                                                 │
│ ⚠️ WARNING: Even with these fixes, ensure:                    │
│    • Input validation & type checking                         │
│    • Proper error handling (don't reveal DB structure)        │
│    • Database permissions are minimal                         │
│    • Regular security audits & penetration testing            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Secure Code Examples by Vulnerability Type

### 1. **SQL INJECTION**

#### ❌ VULNERABLE CODE
```python
def get_user(user_id):
    query = "SELECT * FROM users WHERE id=" + str(user_id)
    cursor.execute(query)
    return cursor.fetchone()
```

#### ✅ SECURE CODE OPTIONS

**Option A: Parameterized Query (sqlite3/MySQL/PostgreSQL)**
```python
def get_user(user_id):
    # Using ? placeholder
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    return cursor.fetchone()

# Or with named parameters (PostgreSQL)
cursor.execute("SELECT * FROM users WHERE id=%(id)s", {"id": user_id})
```

**Option B: SQLAlchemy ORM**
```python
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import Session

def get_user(user_id):
    with Session(engine) as session:
        user = session.query(User).filter(User.id == user_id).first()
    return user
```

**Option C: Django ORM**
```python
def get_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        return user
    except User.DoesNotExist:
        return None
```

#### ⚠️ ADDITIONAL SECURITY MEASURES
- ✓ Validate input type (ensure it's an integer)
- ✓ Use prepared statements/parameterized queries
- ✓ Set proper database permissions (least privilege)
- ✓ Log queries for audit trails
- ✓ Use connection pooling for performance

---

### 2. **PICKLE VULNERABILITIES**

#### ❌ VULNERABLE CODE
```python
import pickle

# Insecure deserialization
data = pickle.loads(untrusted_data)

# Or loading from file
with open('data.pkl', 'rb') as f:
    data = pickle.load(f)
```

#### ✅ SECURE CODE OPTIONS

**Option A: Use JSON instead (SAFEST)**
```python
import json

# Serialize
data = json.dumps({"key": "value"})

# Deserialize
data = json.loads(data)
```

**Option B: Validate Pickled Objects**
```python
import pickle

class RestrictedPickle(pickle.Unpickler):
    def find_class(self, module, name):
        # Whitelist safe classes only
        if module == "myapp.models" and name in ["User", "Product"]:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"Unsafe class: {module}.{name}")

# Use it
data = RestrictedPickle(file_handle).load()
```

**Option C: Use safer serialization libraries**
```python
import msgpack
# msgpack is safer than pickle for untrusted data
data = msgpack.packb({"key": "value"})
decoded = msgpack.unpackb(data)
```

#### ⚠️ ADDITIONAL SECURITY MEASURES
- ✓ NEVER pickle untrusted data
- ✓ Prefer JSON/MessagePack for external data
- ✓ If pickle is necessary, use RestrictedUnpickler
- ✓ Validate file origins before deserialization
- ✓ Keep Python/libraries updated for security patches

---

### 3. **EVAL USAGE**

#### ❌ VULNERABLE CODE
```python
user_code = request.args.get('code')
result = eval(user_code)  # EXTREMELY DANGEROUS

# Or with exec
exec(user_provided_string)
```

#### ✅ SECURE CODE OPTIONS

**Option A: Use ast.literal_eval (Safe ✓)**
```python
import ast

user_input = "{'key': 'value'}"
try:
    result = ast.literal_eval(user_input)
except (ValueError, SyntaxError):
    result = None
```

**Option B: Expression Parsing with Limited Operations**
```python
from numexpr import evaluate
import numpy as np

# Safe expression evaluation for math
expr = "array1 + array2 * 3"
result = evaluate(expr)
```

**Option C: Custom Parser (Best Control)**
```python
from pyparsing import Word, nums, alphas, opAssoc, opType, infixNotation

def safe_eval(expr_string):
    # Define allowed operations
    number = Word(nums).setParseAction(lambda t: float(t[0]))
    operand = number
    
    expr = infixNotation(operand, [
        ("+", 2, opAssoc.LEFT),
        ("-", 2, opAssoc.LEFT),
        ("*", 2, opAssoc.LEFT),
        ("/", 2, opAssoc.LEFT),
    ])
    
    return expr.parseString(expr_string)[0]
```

#### ⚠️ ADDITIONAL SECURITY MEASURES
- ✓ NEVER use eval() on user input EVER
- ✓ Use ast.literal_eval() for Python literals only
- ✓ Use restricted evaluation libraries
- ✓ Implement whitelisting for allowed operations
- ✓ Create sandboxed environments if dynamic code is needed

---

### 4. **HARDCODED CREDENTIALS**

#### ❌ VULNERABLE CODE
```python
DB_PASSWORD = "admin123"
API_KEY = "sk-17d3c8a9b2f4e6g9h0i1j2k3l4m5n6o7"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

conn = connect(host="localhost", user="admin", password=DB_PASSWORD)
```

#### ✅ SECURE CODE OPTIONS

**Option A: Environment Variables**
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file (NOT in version control)

DB_PASSWORD = os.getenv("DB_PASSWORD")
API_KEY = os.getenv("API_KEY")
AWS_SECRET = os.getenv("AWS_SECRET")

conn = connect(host=os.getenv("DB_HOST"), 
               user=os.getenv("DB_USER"), 
               password=DB_PASSWORD)
```

**Option B: AWS Secrets Manager**
```python
import boto3

secrets_client = boto3.client('secretsmanager')

response = secrets_client.get_secret_value(SecretId='prod/db/password')
db_password = response['SecretString']
```

**Option C: HashiCorp Vault**
```python
import hvac

client = hvac.Client(url='http://127.0.0.1:8200', token='s.XXXXXXXXXXXX')
secret = client.secrets.kv.v2.read_secret_version(path='db/credentials')
db_password = secret['data']['data']['password']
```

#### ⚠️ ADDITIONAL SECURITY MEASURES
- ✓ Use .env files (add to .gitignore)
- ✓ Use paid secret management services
- ✓ Rotate credentials regularly
- ✓ Use IAM roles instead of credentials when possible
- ✓ Enable audit logging for credential access
- ✓ Never commit secrets to git (even in history!)

---

### 5. **WEAK CRYPTOGRAPHY (MD5/SHA1)**

#### ❌ VULNERABLE CODE
```python
import hashlib

# Weak hashing for passwords
password_hash = hashlib.md5(password.encode()).hexdigest()

# Or using SHA1
password_hash = hashlib.sha1(password.encode()).hexdigest()
```

#### ✅ SECURE CODE OPTIONS

**Option A: bcrypt (RECOMMENDED)**
```python
import bcrypt

# Hashing
password = "mypassword123"
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode(), salt)

# Verification
if bcrypt.checkpw(password.encode(), hashed):
    print("Password matches!")
```

**Option B: Argon2 (Modern & Secure)**
```python
from argon2 import PasswordHasher

hasher = PasswordHasher()

# Hashing
hashed_password = hasher.hash("mypassword123")

# Verification
try:
    hasher.verify(hashed_password, "mypassword123")
    print("Password matches!")
except:
    print("Invalid password")
```

**Option C: PBKDF2 (Standard Library)**
```python
import hashlib
import secrets

# Hashing
password = "mypassword123"
salt = secrets.token_hex(32)
hash_obj = hashlib.pbkdf2_hmac('sha256', 
                               password.encode(), 
                               salt.encode(), 
                               iterations=100000)
hashed = hash_obj.hex()

# Store as: f"{salt}${hashed}"
```

#### ⚠️ ADDITIONAL SECURITY MEASURES
- ✓ Use bcrypt or Argon2 for passwords
- ✓ Use sha256+ for non-password hashing
- ✓ Add random salt (bcrypt does this)
- ✓ Use high iteration counts (bcrypt: 12+)
- ✓ Never reuse salts
- ✓ Implement rate limiting on login attempts

---

### 6. **DEBUG MODE ENABLED**

#### ❌ VULNERABLE CODE
```python
# Flask
app = Flask(__name__)
app.run(debug=True)  # Shows stack traces, secrets in error pages

# Django
DEBUG = True  # In settings.py
```

#### ✅ SECURE CODE OPTIONS

**Option A: Environment-based Debug**
```python
import os

# Flask
app = Flask(__name__)
app.config['DEBUG'] = os.getenv('DEBUG', 'False') == 'True'
app.run()

# Django (settings.py)
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

**Option B: Production Safe Configuration**
```python
# Flask
from flask import Flask, jsonify

app = Flask(__name__)

@app.errorhandler(Exception)
def handle_error(error):
    # Don't expose details in production
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=False)
```

**Option C: Django Best Practices**
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
        },
    },
}
```

#### ⚠️ ADDITIONAL SECURITY MEASURES
- ✓ Always disable debug in production
- ✓ Log errors securely to file/service
- ✓ Set up centralized logging (ELK, CloudWatch)
- ✓ Monitor error logs for attack patterns
- ✓ Use error tracking services (Sentry)

---

## ⚠️ SECURITY DISCLAIMER TEMPLATE

```
┌─────────────────────────────────────────────────────────────────┐
│ ⓘ SECURITY DISCLAIMER                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ The secure code examples provided are REFERENCE IMPLEMENTATIONS │
│ and may not be suitable for all contexts. Security depends on: │
│                                                                 │
│ • Your specific application architecture & requirements        │
│ • Proper input validation and sanitization                     │
│ • Network security and access control measures                 │
│ • Regular security audits and penetration testing              │
│ • Keeping libraries and frameworks up-to-date                  │
│ • Proper error handling & logging practices                    │
│                                                                 │
│ 100% SECURITY CANNOT BE GUARANTEED. This tool helps identify   │
│ common vulnerabilities but should be part of a comprehensive   │
│ security strategy including:                                   │
│                                                                 │
│ ✓ Code reviews by security experts                             │
│ ✓ Static & dynamic analysis tools                              │
│ ✓ Dependency vulnerability scanning                            │
│ ✓ Security testing (SAST, DAST)                                │
│ ✓ Incident response planning                                   │
│                                                                 │
│ Always consult with your security team before deployment.     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## No Secure Code Available

**When to show this message:**

```
Some vulnerabilities may not have direct code fixes, such as:
• Architectural issues requiring redesign
• Configuration problems (server setup)
• Process/policy violations
• Complex business logic concerns

FOR THIS VULNERABILITY:
No automated secure code example could be generated. Consider:
1. Review the vulnerability details above
2. Consult with your security team
3. Implement security review process for this module
4. Add integration tests for this concern
```

---

## Integration Steps

### Step 1: Add to Vulnerability Response Model
```python
# backend/models.py
class VulnerabilityDetail(BaseModel):
    id: str
    type: str
    severity: str
    original_line: str
    original_code: str
    vulnerability_explanation: str
    how_to_fix: List[str]
    secure_code_examples: List[CodeExample]  # NEW
    warning_text: str  # NEW
    
class CodeExample(BaseModel):
    title: str
    method: str
    code: str
    language: str = "python"
```

### Step 2: Update Frontend Component
```javascript
// VulnerabilityDetail.jsx
<div className="vulnerability-card">
  <SecurityDisclaimer />
  
  <OriginalCode code={vuln.original_code} />
  
  <VulnerabilityAnalysis analysis={vuln.vulnerability_explanation} />
  
  <HowToFix fixes={vuln.how_to_fix} />
  
  <SecureCodeSection examples={vuln.secure_code_examples} />
  
  <WarningFooter text={vuln.warning_text} />
</div>
```

---

## Next Steps

1. ✅ Review this guide with your security team
2. ✅ Implement UI components for secure code display
3. ✅ Update backend to generate these examples
4. ✅ Add comprehensive testing for recommendations
5. ✅ Create documentation for developers
6. ✅ Monitor for false positives/unnecessary alerts

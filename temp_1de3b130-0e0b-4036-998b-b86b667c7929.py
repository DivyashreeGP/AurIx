# 1. SQL Injection
import sqlite3
conn = sqlite3.connect(':memory:')
user_input = "' OR '1'='1"
query = f"SELECT * FROM users WHERE username = '{user_input}'"
conn.execute(query)

# 2. Command Injection
import subprocess
filename = "test.txt; rm -rf /"
subprocess.call(f"cat {filename}", shell=True)

# 3. Hard-coded Credentials
api_key = "sk-1234567890abcdefghijklmnop"
password = "admin123"
database_url = "postgres://user:secretpassword@localhost/db"

# 4. Insecure Deserialization
import pickle
data = b'\x80\x04\x95\x05\x00\x00\x00\x00\x00\x00\x00\x8c\x05test\x94.'
obj = pickle.loads(data)

# 5. Eval with User Input
user_code = "print('hello')"
eval(user_code)

# 6. Path Traversal Vulnerability
import os
user_path = request.args.get('file')  # User sends: ../../etc/passwd
file = open(user_path, 'r')
content = file.read()

# 7. Weak Cryptography
import hashlib
password = "mypassword"
weak_hash = hashlib.md5(password.encode()).hexdigest()

# 8. XXE (XML External Entity) Injection
import xml.etree.ElementTree as ET
xml_input = '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><data>&xxe;</data>'
tree = ET.fromstring(xml_input)

# 9. Weak Random Number Generation for Security
import random
token = random.randint(1, 1000000)
session_id = str(random.random())

# 10. Unvalidated Redirect
from flask import redirect, request
return redirect(request.args.get('next', '/'))
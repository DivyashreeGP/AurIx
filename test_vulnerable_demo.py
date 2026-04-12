"""
Vulnerable Code Example - Should Be Detected by Advanced System
Tests: Real vulnerabilities that should be caught
"""

import pickle
import os
import subprocess
import sqlite3

def vulnerable_eval_code(user_input):
    """VULNERABLE: Direct eval without validation"""
    result = eval(user_input)  # Direct eval - CODE INJECTION
    return result


def vulnerable_pickle_load(data):
    """VULNERABLE: Unsafe pickle deserialization"""
    return pickle.loads(data)  # UNSAFE DESERIALIZATION


def vulnerable_command_injection(filename):
    """VULNERABLE: Command injection via os.system"""
    os.system(f"rm {filename}")  # COMMAND INJECTION - no validation


def vulnerable_sql_injection(user_id):
    """VULNERABLE: SQL injection"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL INJECTION
    cursor.execute(query)
    return cursor.fetchall()


def vulnerable_hardcoded_credentials():
    """VULNERABLE: Hardcoded credentials"""
    api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"  # HARDCODED API KEY
    password = "MySecurePassword123"  # HARDCODED PASSWORD
    db_conn = "postgresql://admin:P@ssw0rd@localhost:5432/mydb"  # HARDCODED CONNECTION
    return api_key, password, db_conn


def vulnerable_subprocess(user_input):
    """VULNERABLE: Subprocess with user input"""
    subprocess.call(f"grep {user_input} /etc/passwd", shell=True)  # COMMAND INJECTION


def vulnerable_file_traversal(filename):
    """VULNERABLE: Path traversal vulnerability"""
    with open(f"/tmp/{filename}", 'r') as f:  # No validation - PATH TRAVERSAL
        return f.read()


def vulnerable_xxe(xml_data):
    """VULNERABLE: XML External Entity attack"""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_data)  # XXE VULNERABILITY
    return root


def vulnerable_weak_crypto():
    """VULNERABLE: Weak cryptography"""
    import hashlib
    password = "user_password"
    hashed = hashlib.md5(password.encode()).hexdigest()  # MD5 IS WEAK
    return hashed


def vulnerable_insecure_random():
    """VULNERABLE: Insecure random for security"""
    import random
    token = random.randint(1, 1000)  # INSECURE RANDOM - not secrets
    return token


if __name__ == "__main__":
    print("⚠️  This file contains intentional vulnerabilities for testing!")

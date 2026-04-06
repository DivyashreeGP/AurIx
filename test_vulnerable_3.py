#!/usr/bin/env python3
"""
Test file 3: Command Injection & Weak Crypto
Paste this code after test_vulnerable_2.py
UI should update showing shell=True and MD5 vulnerabilities
"""

import subprocess
import hashlib
import os

def run_command(user_command):
    """VULNERABLE: Command injection via shell=True"""
    result = subprocess.call(user_command, shell=True)
    return result

def hash_password(password):
    """VULNERABLE: Using weak MD5 hash for passwords"""
    weak_hash = hashlib.md5(password.encode()).hexdigest()
    return weak_hash

def verify_credentials():
    """VULNERABLE: Hardcoded credentials"""
    api_key = "sk-1234567890abcdefghijklmnop"
    password = "admin123"
    
    # Some verification logic
    if password == "admin123":
        return True
    return False

if __name__ == "__main__":
    # Examples of vulnerable calls
    run_command("ls -la")
    pwd_hash = hash_password("user_password")
    verify_credentials()

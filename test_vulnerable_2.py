#!/usr/bin/env python3
"""
Test file 2: SQL Injection
Paste this code after test_vulnerable_1.py
The UI should update and show different results (SQL instead of Pickle)
"""

import sqlite3

def query_user_by_id(user_id):
    """VULNERABLE: SQL Injection - Using string formatting instead of parameterized query"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # VULNERABLE: Direct string interpolation
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    
    return cursor.fetchall()

def get_password_with_eval(password_input):
    """VULNERABLE: Using eval() on user input"""
    result = eval(password_input)
    return result

if __name__ == "__main__":
    # These would be vulnerable if called with untrusted input
    user_data = query_user_by_id("1' OR '1'='1")
    print(user_data)

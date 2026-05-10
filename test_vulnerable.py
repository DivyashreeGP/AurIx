# Vulnerable code examples that SHOULD be flagged

# 1. SQL Injection - vulnerable
def vulnerable_sql(user_input):
    query = "SELECT * FROM users WHERE id = " + user_input
    cursor.execute(query)

# 2. Command Injection - vulnerable
import os
def vulnerable_cmd(user_input):
    os.system("ls " + user_input)

# 3. Path Traversal - vulnerable
def vulnerable_file(user_input):
    with open("/var/www/uploads/" + user_input) as f:
        return f.read()

# 4. Hard-coded credentials - vulnerable
def vulnerable_auth():
    password = "secret123"

# 5. Eval injection - vulnerable
def vulnerable_eval(user_input):
    eval(user_input)

# 6. Pickle deserialization - vulnerable
import pickle
def vulnerable_pickle(data):
    obj = pickle.loads(data)
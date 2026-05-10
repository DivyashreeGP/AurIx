import os
import subprocess

def safe_query(user_input):
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_input,))

password = os.getenv("PASSWORD")
if not password:
    raise ValueError("Missing PASSWORD")

def safe_list(directory):
    return os.listdir(directory)
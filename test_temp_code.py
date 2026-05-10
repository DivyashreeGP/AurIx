
import pickle
import random
import hashlib

def insecure_deserialize(user_data):
    # VULNERABLE: pickle.loads with untrusted data
    obj = pickle.loads(user_data)
    return obj

def weak_hash(password):
    # VULNERABLE: MD5 is cryptographically weak
    return hashlib.md5(password.encode()).hexdigest()

def generate_token():
    # VULNERABLE: random module is not cryptographically secure
    return str(random.randint(1000000, 9999999))

api_key = "sk-proj-abc123xyz789"  # VULNERABLE: hardcoded secret

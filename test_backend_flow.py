import requests
import json

# Test secure code
secure_code = '''
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()
'''

response = requests.post('http://localhost:8000/analyze', json={'code': secure_code}, timeout=10)
print('Secure code result:', json.dumps(response.json(), indent=2))
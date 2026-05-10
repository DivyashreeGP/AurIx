import requests
import json

# Test vulnerable code
vulnerable_code = '''
def get_user(user_input):
    query = "SELECT * FROM users WHERE id = " + user_input
    cursor.execute(query)
'''

response = requests.post('http://localhost:8000/analyze', json={'code': vulnerable_code}, timeout=10)
print('Vulnerable code result:', json.dumps(response.json(), indent=2))
import requests
import json

# Test the /analyze-with-ai endpoint
test_code = """import pickle
data = request.args.get('x')
obj = pickle.loads(data)"""

test_issues = [
    {
        "type": "Insecure Deserialization",
        "description": "pickle.loads can deserialize arbitrary code",
        "line": 3,
        "severity": "high",
        "code": "obj = pickle.loads(data)"
    }
]

payload = {
    "code": test_code,
    "issues": test_issues
}

try:
    response = requests.post(
        "http://localhost:8000/analyze-with-ai",
        json=payload,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Type: {type(response.json())}")
    print(f"\nFull Response:")
    print(json.dumps(response.json(), indent=2)[:500])
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

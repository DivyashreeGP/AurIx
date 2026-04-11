# Quick Start Guide - AurIx AI Analysis

## 🚀 Getting Started in 5 Minutes

### Step 1: Start the Backend
```powershell
cd c:\Major_Project\Integration\AurIx
.\venv\Scripts\activate
cd backend
python -m uvicorn main:app --reload --port 8000
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Set Claude API Key (Optional but Recommended)
```powershell
# In PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"

# Verify it's set
Write-Host $env:ANTHROPIC_API_KEY
```

Get your key from: https://console.anthropic.com/api-keys

### Step 3: Reload Extension in VS Code
- Press `Ctrl+R` in the Extension Development Host window (the secondary VS Code window)
- This reloads the extension from your latest code

### Step 4: Test with Vulnerable Code
Create a new Python file (or open an existing one) and paste this:

```python
import pickle
data = request.args.get('user_data')
obj = pickle.loads(data)
print(obj)
```

### Step 5: Trigger Analysis
Press `Ctrl+S` (or `Cmd+S` on Mac) to save.

**Expected Result:**
1. Red squiggly line appears under `pickle.loads`
2. A new panel opens on the right with AurIx Analysis
3. You'll see:
   - **🔍 Vulnerability Analysis**: Explains why this is dangerous
   - **✅ Secure Code**: Shows fixed version using `json` instead
   - **📚 Explanation**: Step-by-step fix explanation

## 📋 How the System Works

```
1. You save a Python file (Ctrl+S)
   ↓
2. Extension detects vulnerabilities (regex + AST)
   ↓
3. Sends code + vulnerabilities to backend
   ↓
4. Backend sends to Claude AI for analysis
   ↓
5. Claude returns: Why-it's-bad + Fixed-code + Explanation
   ↓
6. Results displayed in beautiful VS Code panel
```

## 🔧 System Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Extension** | `vscode_extension/vs-extension/src/extension.ts` | Detects issues, calls backend |
| **Backend API** | `backend/main.py` | Runs detection engine, calls Claude |
| **Detection** | `detect.py` | Scans for vulnerabilities |
| **Rules** | `Rule_Engine/ruleset/*.json` | Defines vulnerability patterns |
| **UI** | `extension.ts` (webview) | Shows analysis in panel |

## 🧪 Test Cases

Try these codes (Save each one and check detection):

```python
# Test 1: Hard-coded Credentials
API_KEY = "sk-1234567890abcdefghijk"
password = "admin123"
```

```python
# Test 2: Command Injection
import subprocess
cmd = f"cat {user_file}"
subprocess.call(cmd, shell=True)
```

```python
# Test 3: Eval Usage
user_input = input("Enter code: ")
eval(user_input)
```

```python
# Test 4: Unsafe Deserialization
import pickle
user_data = request.args.get('data')
obj = pickle.loads(user_data)
```

```python
# Test 5: SQL Injection
user_id = request.args.get('id')
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)
```

## 🐛 Troubleshooting

### Analysis panel doesn't appear
- ✅ Check: Is backend running? (Should see uvicorn message)
- ✅ Check: Is your code actually vulnerable? (Should have red squiggly lines)
- ✅ Check: Did you press Ctrl+S? (This triggers AI analysis)

### Error: "Failed to connect to AI analysis engine"
- ✅ Backend not running
  ```powershell
  # Start it again in backend folder
  python -m uvicorn main:app --reload --port 8000
  ```

### Error: "AI analysis failed: 401 Unauthorized"
- ✅ Claude API key is wrong or not set
- ✅ Get key from: https://console.anthropic.com/api-keys
- ✅ Set it: `$env:ANTHROPIC_API_KEY = "your-key"`

### No vulnerabilities detected
- ✅ Code might not match detection rules
- ✅ Try using examples from Test Cases above
- ✅ Check if file is saved as `.py`

## 💡 Tips

- **Keyboard Shortcut**: Ctrl+S saves + triggers analysis
- **Alternative**: Ctrl+Shift+A can manually trigger analysis
- **Copy Code**: Click "📋 Copy Code" button in the panel
- **Tabs**: Switch between Analysis, Code, and Explanation tabs
- **Real-time**: Errors show immediately as you type (not just on save)

## 🔐 Privacy

- Only detected vulnerabilities + code snippet sent to Claude
- Nothing stored on servers (stateless)
- API calls go directly to Anthropic

## ✅ Checklist

Before troubleshooting, verify:
- [ ] Backend is running (`uvicorn main:app`)
- [ ] Claude API key is set (`$env:ANTHROPIC_API_KEY`)
- [ ] File is saved as `.py`
- [ ] Code contains actual vulnerabilities
- [ ] You pressed Ctrl+S to save
- [ ] VS Code shows red error squiggles

## 🎯 Next Steps

1. Try the test cases above
2. If it works - share it! 🎉
3. If issues - check troubleshooting section
4. Want to customize? Edit rules in `Rule_Engine/ruleset/`

---

**Ready?** Follow Step 1 and you're good to go!

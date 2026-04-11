# AurIx AI Analysis Setup Guide

## Overview
Your AurIx extension now includes real-time vulnerability detection with AI-powered analysis and secure code fixes!

## Features
✅ **Real-time Detection** - Detects vulnerabilities as you type  
✅ **AI Analysis** - Press Ctrl+S to send code to AI engine  
✅ **Secure Code Fixes** - Get corrected code with explanations  
✅ **Copilot-like UI** - Beautiful analysis panel in VS Code  

## How to Use

### 1. **Real-time Vulnerability Highlighting**
- Paste or type Python code
- Vulnerabilities appear as red/yellow squiggly lines
- Hover over them to see the issue

### 2. **AI Analysis (Main Feature)**
- **Press Ctrl+S** (or Cmd+S on Mac) to save the file
- The extension automatically sends vulnerabilities + code to the AI engine
- An analysis panel opens showing:
  - 🔍 **Vulnerability Analysis** - Why it's a security risk
  - ✅ **Secure Code** - Corrected version with fixes
  - 📚 **Explanation** - Step-by-step explanation of fixes

### 3. **Manual Trigger**
- Run command: `AurIx: Analyze with AI` (Ctrl+Shift+A on Windows/Linux, Cmd+Shift+A on Mac)

## Setup Requirements

### Backend (FastAPI)
Make sure the backend is running:
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Claude API Key (for AI Analysis)
The system currently uses Claude API for AI analysis. To enable full AI features:

**Option 1: Set Environment Variable**
```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "your-api-key-here"

# Windows CMD
set ANTHROPIC_API_KEY=your-api-key-here

# macOS/Linux
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Option 2: Add to .env file in backend directory**
Create `.env` in the backend folder:
```
ANTHROPIC_API_KEY=your-api-key-here
```

Then update `main.py` to load it:
```python
import os
from dotenv import load_dotenv
load_dotenv()
```

### Get Claude API Key
1. Go to https://console.anthropic.com
2. Create an account or login
3. Navigate to API Keys
4. Create a new API key
5. Copy and set it as shown above

## Troubleshooting

### Issue: "Failed to connect to AI analysis engine"
- ✅ Ensure backend is running on `localhost:8000`
- ✅ Check if FastAPI server is started

### Issue: "AI analysis failed"
- ✅ Check Claude API key is set correctly
- ✅ Verify API key has sufficient credits
- ✅ Check network connectivity

### Issue: Detection not showing
- ✅ Make sure you're editing a `.py` file
- ✅ Press Ctrl+S to trigger analysis
- ✅ Check if Express server is running

## Architecture

```
VS Code Extension (TypeScript)
        ↓
   Saves code (Ctrl+S)
        ↓
FastAPI Backend (Python)
        ↓
Detection Engine (Regex + AST)
        ↓
Claude AI (LLM)
        ↓
Webview Panel (Copilot-like UI)
```

## What Gets Sent to AI?
- Your code snippet
- Detected vulnerabilities with line numbers
- Vulnerability types and descriptions

**Privacy Note:** The code is only sent to Claude API. Ensure your API key is kept secret.

## Example Workflow

```python
# Paste this code and press Ctrl+S
import pickle
data = request.args.get('data')
obj = pickle.loads(data)
```

You'll see:
1. Red squiggly line under `pickle.loads`
2. Analysis panel opens with:
   - Why pickle.loads is dangerous
   - Secure alternative using json
   - Step-by-step fix explanation

## Customization

### Change AI Prompt
Edit `backend/main.py` in the `analyze_with_ai()` function to customize the analysis prompt.

### Change Detection Rules
Edit JSON files in `Rule_Engine/ruleset/` to add/modify detection patterns.

### Customize UI
Edit the HTML/CSS in `extension.ts` in the `getWebviewContent()` function.

## Next Steps
1. ✅ Start the backend: `python -m uvicorn main:app --reload --port 8000`
2. ✅ Set your Claude API key
3. ✅ Reload the Extension Development Host (Ctrl+R)
4. ✅ Paste vulnerable code and press Ctrl+S
5. ✅ Review the AI analysis in the panel

---

For questions or issues, check the console output: `View → Output → AurIx`

# 🔍 AurIx Analysis Flow - Where Secure Code & Explanation Come From

## 📊 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  VS Code Extension (Frontend)                                   │
│  User saves code → Extension analyzes                           │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP POST /analyze
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  backend/main.py - @app.post("/analyze")                        │
│  1. Receives code from extension                                │
│  2. Saves to temp file                                          │
│  3. Calls detect.py to find vulnerabilities                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  detect.py (Vulnerability Scanner)                              │
│  - Pattern matching against Rule_Engine/ruleset/*.json files    │
│  - AST analysis for taint tracking                              │
│  - Returns: list of detected vulnerabilities                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  backend/main.py - @app.post("/analyze-with-ai")                │
│  Takes code + vulnerabilities                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────┴─────┐
                    ▼          ▼
        ┌────────────────┐  ┌──────────────────┐
        │ LOCAL_AI=True  │  │ LOCAL_AI=False   │
        │ (Ollama avail) │  │ (Use Template)   │
        └────────┬───────┘  └────────┬─────────┘
                 │                    │
                 ▼                    ▼
        ┌──────────────────┐  ┌──────────────────────┐
        │ AI ENGINE (LLM)  │  │ TEMPLATE RESPONSE    │
        │ Ollama/Qwen2.5   │  │ (Hard-coded rules)   │
        └────────┬─────────┘  └──────────┬───────────┘
                 │                       │
    ┌────────────┼────────────┐          │
    │            │            │          │
    ▼            ▼            ▼          ▼
   SECURE     ANALYSIS    EXPLANATION   TEMPLATE
    CODE      (JSON)      (Markdown)   (Fallback)
```

## 📍 Source Locations

### 1️⃣ **Secure Code** - Where it comes from

**When AI Ollama is available:**
- **File:** `AI-Reasoning-Engine/ai_security_analyzer/app/secure_generator.py`
- **Function:** `generate_secure_code(code, vulnerabilities)`
- **Logic:** 
  - Creates prompt with original code + detected issues
  - Sends to Ollama LLM (Qwen 2.5 model)
  - LLM returns fixed, secured code
  - Backend returns the response as-is

**When AI is NOT available (fallback):**
- **File:** `backend/main.py` → `generate_template_response()` function
- **Logic:**
  - Searches for known vulnerability patterns
  - Applies hardcoded fixes (pickle→json, eval→ast.literal_eval, etc.)
  - Generates improved code automatically
  - Location: Lines ~340-430 in main.py

### 2️⃣ **Explanation** - Where it comes from

**When AI Ollama is available:**
- **File:** `AI-Reasoning-Engine/ai_security_analyzer/app/reasoning.py`
- **Function:** `generate_explanation(code, vulnerabilities)`
- **Logic:**
  - Creates structured JSON prompt
  - Sends to Ollama LLM with vulnerability details
  - LLM returns JSON with detailed analysis:
    - `type`: Vulnerability type
    - `line`: Line number
    - `cause`: Why the code is vulnerable
    - `risk`: Security impact
    - `fix`: How to fix it
    - `severity`: High/Critical/Medium/Low
  - Backend formats into Markdown sections
  - Frontend displays with HTML rendering

**When AI is NOT available (fallback):**
- **File:** `backend/main.py` → `generate_template_response()` function
- **Data:** `vuln_explanations` dictionary (Lines ~310-335)
- **Mapping:**
  ```python
  vuln_explanations = {
      "pickle.loads": {
          "risk": "Arbitrary Code Execution (ACE)",
          "why": "pickle.loads() can deserialize...",
          "impact": "Complete system compromise...",
          "fix": "Use json.loads()...",
          "secure": "obj = json.loads(user_data)"
      },
      # ... more patterns
  }
  ```
- **Logic:** Matches detected vulnerabilities to explanations, builds markdown

## 🔄 Complete Request/Response Chain

```json
REQUEST:
{
  "code": "import pickle\ndata = pickle.loads(...)"
}
     ↓
DETECT VULNERABILITIES (detect.py):
{
  "pickle_unsafe_deserialize": {
    "line": 2,
    "type": "INSECURE_DESERIALIZATION"
  }
}
     ↓
AI ANALYSIS (/analyze-with-ai):
{
  "code": "import pickle\ndata = pickle.loads(...)",
  "issues": [
    {
      "type": "INSECURE_DESERIALIZATION",
      "line": 2,
      "description": "..."
    }
  ]
}
     ↓
RESPONSE (from LLM or template):
{
  "secure_code": "import json\ndata = json.loads(...)",
  "explanation": "### Arbitrary Code Execution (ACE)\n\n**Cause:** pickle.loads()...",
  "analysis": "..."
}
```

## 🎯 Key Files & Responsibilities

| File | Purpose | Output |
|------|---------|--------|
| `detect.py` | Find vulnerabilities | JSON list of issues |
| `backend/main.py` | Orchestrate analysis | HTTP responses |
| `reasoning.py` | Generate detailed explanation | Markdown formatted text |
| `secure_generator.py` | Generate fixed code | Python code |
| `llm_client.py` | Call Ollama/LLM | Raw LLM response |
| `config.py` | LLM configuration | Ollama connection details |

## 🔐 Two Analysis Paths

### Path A: With Ollama (Recommended)
```
Code → Detect → AI Analysis → Ollama LLM → Secure Code + Explanation
```
- More accurate fixes
- Better explanations
- Requires Ollama running

### Path B: Without Ollama (Fallback)
```
Code → Detect → Template Rules → Pattern Matching → Secure Code + Explanation
```
- Works offline
- Faster response
- Pre-built explanations

## 📝 How Frontend Gets Results

1. Extension saves code
2. Backend `/analyze` endpoint runs `detect.py`
3. If issues found → calls `/analyze-with-ai`
4. Response is formatted and sent to extension
5. Extension's `parseMarkdownToHtml()` converts explanation to beautiful HTML
6. Displayed in "How to Fix" panel with styling

---

**TL;DR:**
- **Secure Code** = Generated by Ollama LLM or hardcoded patterns in `generate_template_response()`
- **Explanation** = Generated by Ollama LLM's JSON output or template dictionary in `vuln_explanations`
- **Flow** = Extension → Backend → Detect → AI/Template → Response → Frontend Display

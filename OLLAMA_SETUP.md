# Local AI Model Setup - Ollama + Qwen 2.5

## 🎯 No API Keys Required!

Your project now uses a **local AI model** (Qwen 2.5 7B) running on your machine via Ollama.

**Benefits:**
- ✅ No API keys needed
- ✅ Runs completely offline (after download)
- ✅ Free and open-source
- ✅ Full privacy - data stays on your machine
- ✅ Fast analysis

---

## 📦 Step 1: Download Ollama

### Windows

1. Go to https://ollama.ai (or https://ollama.com)
2. Download "Ollama for Windows"
3. Install it (follows standard Windows installer)
4. Ollama will run automatically as a service

### macOS

```bash
# Install via Homebrew
brew install ollama

# Start Ollama
ollama serve
```

### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

---

## 🤖 Step 2: Download the Qwen 2.5 Model

Open a **new terminal** (your Ollama server should be running in the background):

```bash
ollama pull qwen2.5:7b
```

This downloads the model (~4.7 GB). Wait for it to complete.

**Expected output:**
```
pulling manifest
pulling 8934d4e224f1... 100% ▕████████████████▏
pulling 8b98b4f4f...... 100% ▕████████████████▏
Verifying sha256 digest
Writing manifest
Success
```

---

## ✅ Step 3: Verify Ollama is Running

In a terminal, run:

```bash
curl http://localhost:11434/api/generate -d '{"model":"qwen2.5:7b","prompt":"hello"}'
```

**Expected response:**
```json
{"model":"qwen2.5:7b","created_at":"...","response":"Hello! How can I help you today?", ...}
```

If you see this → **Ollama is working!** ✅

---

## 🔧 Step 4: Start Your Backend

With Ollama running in the background:

```powershell
cd c:\Major_Project\Integration\AurIx
.\venv\Scripts\activate
cd backend
python -m uvicorn main:app --reload --port 8000
```

You should see in the logs:
```
DeVAIC: Using Local AI Engine (Qwen 2.5) for analysis...
```

---

## 🚀 Step 5: Test the Complete System

1. **Keep 3 terminals open:**
   - Terminal 1: Ollama running (started with `ollama serve`)
   - Terminal 2: Backend running (started with `uvicorn`)
   - Terminal 3: VS Code Extension Development Host (reload with Ctrl+R)

2. **Test in VS Code:**
   - Paste this code:
   ```python
   import pickle
   user_data = request.args.get('data')
   obj = pickle.loads(user_data)
   ```
   
   - Press **Ctrl+S**
   
   - Watch the analysis panel appear with:
     - Vulnerability explanation
     - Secure code fix
     - Step-by-step fix guide

---

## 🔍 Architecture

```
VS Code Extension
        ↓
 (Ctrl+S to save)
        ↓
FastAPI Backend
        ↓
Local AI Reasoning Engine
        ↓
Ollama + Qwen 2.5 (Local LLM)
        ↓
Analysis Results
        ↓
Webview Panel (Results)
```

---

## 📊 Performance

| Model | Speed | Quality | Size | Memory |
|-------|-------|---------|------|--------|
| Qwen 2.5 7B | Medium | Good | 4.7 GB | 8+ GB RAM |
| Qwen 2.5 1B | Fast | Fair | 650 MB | 2+ GB RAM |

**Recommendation:** Use 7B for better quality (requires 8GB+ RAM)

---

## 🐛 Troubleshooting

### "Failed to connect to AI analysis engine"

**Check if Ollama is running:**
```bash
curl http://localhost:11434/api/generate
```

**If not running:**
- Windows: Ollama runs as service. Check system tray or restart.
- Mac/Linux: Run `ollama serve` in a terminal

---

### "Local AI analysis failed"

**Possible causes:**

1. **Model not downloaded:**
   ```bash
   ollama pull qwen2.5:7b
   ```

2. **Ollama port in use:**
   - Default: `localhost:11434`
   - Check if something else is using port 11434

3. **Not enough RAM:**
   - Qwen 7B needs 8GB+ RAM
   - Use smaller model: `ollama pull qwen2.5:1b`

---

### "Model running but slow"

**Optimize:**

1. **Use 1B model (faster):**
   ```bash
   ollama pull qwen2.5:1b
   
   # Update config.py
   MODEL = "qwen2.5:1b"
   ```

2. **Close other apps** to free up RAM

3. **Use GPU acceleration:**
   - Ollama auto-detects CUDA/Metal
   - Ensure drivers are updated

---

## 📝 Configuration

Edit `AI-Reasoning-Engine/ai_security_analyzer/app/config.py`:

```python
class Config:
    MODEL = "qwen2.5:7b"  # <- Change model here
    BASE_URL = "http://localhost:11434/api/generate"
    
    TEMPERATURE_REASONING = 0.3  # Lower = more focused
    TEMPERATURE_CODE = 0.2       # Lower = safer code
    
    MAX_TOKENS = 1024
    CONTEXT_SIZE = 2048
```

---

## 📚 Useful Commands

```bash
# List available models
ollama list

# Show model info
ollama show qwen2.5:7b

# Delete model (free up space)
ollama rm qwen2.5:7b

# Run model directly (testing)
ollama run qwen2.5:7b "Analyze this code: ..."

# Update Ollama
ollama pull # Downloads latest version of all models
```

---

## 🌐 Model Options

### Fast & Lightweight
```bash
ollama pull qwen2.5:1b    # 650 MB, 2GB RAM
ollama pull phi3           # 2.3 GB, 4GB RAM
```

### Balanced (Recommended)
```bash
ollama pull qwen2.5:7b    # 4.7 GB, 8GB RAM (DEFAULT)
```

### High Quality
```bash
ollama pull qwen2.5:14b   # 9 GB, 16GB RAM
ollama pull mistral       # 4.1 GB, 8GB RAM
```

---

## ✨ Features

Your DeVAIC system now:

✅ Detects vulnerabilities in real-time
✅ Analyzes with local AI (no internet needed)
✅ Generates secure code fixes
✅ Explains fixes step-by-step
✅ All offline - complete privacy
✅ Free to use - no API costs

---

## 🎓 Next Steps

1. ✅ Install Ollama
2. ✅ Download Qwen 2.5
3. ✅ Start Ollama server
4. ✅ Start backend
5. ✅ Test with vulnerable code

**You're all set!** 🚀

---

**Need help?** Check the main README or view backend logs:
```
View → Output → Python
```

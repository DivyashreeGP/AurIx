import os
from pathlib import Path
from dotenv import load_dotenv

# Locate project root (2 levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
env_path = BASE_DIR / ".env"
load_dotenv(env_path)

# 🔐 API Key (Optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
if not OPENAI_API_KEY:
    OPENAI_API_KEY = None

# 🤖 Model Configuration (Optional override)
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo-16k")

# Optional base URL for OpenAI-compatible endpoints
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
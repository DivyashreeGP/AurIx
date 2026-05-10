import os
from pathlib import Path
from dotenv import load_dotenv

# Locate project root (2 levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
env_path = BASE_DIR / ".env"
load_dotenv(env_path)

# 🔐 API Key (Optional)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    GEMINI_API_KEY = None

# 🤖 Model Configuration (Optional override)
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
import os

class Config:
    # LLM Configuration
    MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    
    # Support both Docker and local Ollama instances
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "ollama")  # Docker hostname
    OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
    BASE_URL = os.getenv("BASE_URL", f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate")
    
    # Alternative: Support localhost for local development
    if "localhost" not in BASE_URL and "127.0.0.1" not in BASE_URL:
        # For Docker, use the service name
        BASE_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"
    
    TEMPERATURE_REASONING = 0.3
    TEMPERATURE_CODE = 0.2
    
    MAX_TOKENS = 1024
    CONTEXT_SIZE = 2048
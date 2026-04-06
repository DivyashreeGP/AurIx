class Config:
    MODEL = "qwen2.5:7b"
    BASE_URL = "http://localhost:11434/api/generate"
    
    TEMPERATURE_REASONING = 0.3
    TEMPERATURE_CODE = 0.2
    
    MAX_TOKENS = 1024
    CONTEXT_SIZE = 2048
import requests
from app.config import Config


def call_llm(prompt: str, temperature: float):
    try:
        response = requests.post(
            Config.BASE_URL,
            json={
                "model": Config.MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_ctx": Config.CONTEXT_SIZE
                }
            }
        )

        response.raise_for_status()
        return response.json()["response"]

    except Exception as e:
        return f"Error calling local LLM: {str(e)}"
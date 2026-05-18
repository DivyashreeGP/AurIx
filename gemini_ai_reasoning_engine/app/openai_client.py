import json
import re
import requests
from .config import OPENAI_API_KEY, OPENAI_MODEL_NAME, OPENAI_API_BASE


def extract_json(text: str):
    """
    Try to extract valid JSON from model output
    """
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                return None
    return None


def ask_openai(prompt: str, mode: str = "normal"):
    """
    mode:
    - "normal" → return plain text
    - "json"   → ensure valid JSON output
    - "code"   → clean code output
    """

    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not configured")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENAI_MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1500
    }

    try:
        response = requests.post(
            f"{OPENAI_API_BASE}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        if not data or "choices" not in data or len(data["choices"]) == 0:
            raise ValueError("Empty response from OpenAI")

        text = data["choices"][0]["message"]["content"].strip()

        if mode == "json":
            parsed = extract_json(text)
            if parsed is not None:
                return parsed
            return {
                "error": "Invalid JSON format",
                "raw_response": text
            }

        if mode == "code":
            cleaned = re.sub(r"```.*?\n", "", text)
            cleaned = cleaned.replace("```", "").strip()
            return cleaned

        return text

    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else None
        if status == 429:
            raise RuntimeError("OpenAI API rate limit exceeded") from e
        raise RuntimeError(f"OpenAI API failed: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"OpenAI API failed: {str(e)}") from e
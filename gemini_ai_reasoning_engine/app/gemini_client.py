from google import genai
from .config import GEMINI_API_KEY, MODEL_NAME
import json
import re

client = None


def get_client():
    global client
    if client is None:
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key is not configured")
        client = genai.Client(api_key=GEMINI_API_KEY)
    return client


def extract_json(text: str):
    """
    Try to extract valid JSON from model output
    """
    try:
        return json.loads(text)
    except:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return None
    return None


def ask_gemini(prompt: str, mode: str = "normal"):
    """
    mode:
    - "normal" → return plain text
    - "json"   → ensure valid JSON output
    - "code"   → clean code output
    """

    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key is not configured")

    try:
        client = get_client()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response or not hasattr(response, "text") or not response.text:
            raise ValueError("Empty response from model")

        text = response.text.strip()

        # 🔹 MODE: JSON
        if mode == "json":
            parsed = extract_json(text)
            if parsed is not None:
                return parsed
            else:
                return {
                    "error": "Invalid JSON format",
                    "raw_response": text
                }

        # 🔹 MODE: CODE
        elif mode == "code":
            cleaned = re.sub(r"```.*?\n", "", text)
            cleaned = cleaned.replace("```", "").strip()
            return cleaned

        # 🔹 MODE: NORMAL
        return text

    except Exception as e:
        error_msg = str(e)

        # 🔴 Handle Gemini rate limit (429)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            raise RuntimeError("Gemini API rate limit exceeded") from e

        # 🔴 Other errors
        raise RuntimeError(f"Gemini API failed: {error_msg}") from e
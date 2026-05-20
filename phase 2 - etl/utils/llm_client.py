import os
import requests
from dotenv import load_dotenv

from .config import (
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
)

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY_HERE")


def _llm_error(error: Exception) -> str:
    return f"[LLM Error] {type(error).__name__}: {error}"


def _build_messages(prompt: str, system: str = None) -> list:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return messages


def _post_json(url: str, *, payload: dict, headers: dict | None = None) -> requests.Response:
    response = requests.post(url, headers=headers, json=payload, timeout=180)
    response.raise_for_status()
    return response


def call_llm(prompt: str, system: str = None, max_tokens: int = 1500) -> str:
    """
    Unified LLM caller supporting both Ollama and OpenRouter.
    """
    messages = _build_messages(prompt, system)

    if LLM_PROVIDER == "ollama":
        payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
        }
        try:
            response = _post_json(f"{OLLAMA_BASE_URL}/api/chat", payload=payload)
            return response.json()["message"]["content"]
        except Exception as e:
            return _llm_error(e)

    elif LLM_PROVIDER == "openrouter":
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "DW Project",
        }
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": False,
        }
        try:
            response = _post_json(f"{OPENROUTER_BASE_URL}/chat/completions", payload=payload, headers=headers)
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return _llm_error(e)

    else:
        return f"[LLM Error] Unknown provider: {LLM_PROVIDER}"

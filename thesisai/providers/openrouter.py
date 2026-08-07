"""Proveedor OpenRouter (acceso gratis a modelos open source: Llama, DeepSeek, Qwen).

API compatible con OpenAI. Clave gratuita en: https://openrouter.ai/keys
Con modelos '*:free' no se cobra. Sirve como respaldo si Gemini/Groq fallan.
"""
from __future__ import annotations

import requests

from .base import LLMProvider

API = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterProvider(LLMProvider):
    name = "openrouter"

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, system: str, prompt: str, temperature: float = 0.4) -> str:
        payload = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": 8000,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        resp = requests.post(
            API,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://neurotesis.streamlit.app",
                "X-Title": "ThesisAI",
            },
            json=payload,
            timeout=120,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"OpenRouter {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            raise RuntimeError(f"OpenRouter respuesta inesperada: {str(data)[:300]}")

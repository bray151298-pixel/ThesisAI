"""Proveedor Google Gemini (API REST, gratis)."""
from __future__ import annotations

import requests

from .base import LLMProvider

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, system: str, prompt: str, temperature: float = 0.4) -> str:
        url = API.format(model=self.model)
        payload = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": 8192},
        }
        resp = requests.post(
            url,
            params={"key": self.api_key},
            json=payload,
            timeout=120,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError):
            raise RuntimeError(f"Gemini respuesta inesperada: {str(data)[:300]}")

"""Proveedor Ollama (modelos locales, 100% offline y gratis)."""
from __future__ import annotations

import requests

from .base import LLMProvider


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, model: str, host: str):
        self.model = model
        self.host = host.rstrip("/")

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=3)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def generate(self, system: str, prompt: str, temperature: float = 0.4) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "options": {"temperature": temperature},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        resp = requests.post(f"{self.host}/api/chat", json=payload, timeout=300)
        if resp.status_code != 200:
            raise RuntimeError(f"Ollama {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        try:
            return data["message"]["content"].strip()
        except KeyError:
            raise RuntimeError(f"Ollama respuesta inesperada: {str(data)[:300]}")

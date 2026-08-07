"""Enrutador de IAs gratuitas: intenta varias en orden hasta que una responda.

Orden de preferencia: Gemini -> Groq -> Ollama.
Asi, si una gratuita se queda sin cupo, el bot continua con otra.
"""
from __future__ import annotations

import time

from ..config import settings
from .base import LLMProvider
from .gemini import GeminiProvider
from .groq import GroqProvider
from .openrouter import OpenRouterProvider
from .ollama import OllamaProvider


class LLMError(RuntimeError):
    """Ningun proveedor de IA pudo responder."""


# Errores temporales que conviene reintentar (sobrecarga/limite momentaneo).
_TRANSIENT = (
    "503", "429", "overload", "unavailable", "timeout", "timed out",
    "temporar", "exhausted", "rate limit", "try again",
)


def _is_transient(msg: str) -> bool:
    m = msg.lower()
    return any(t in m for t in _TRANSIENT)


def _all_providers() -> list[LLMProvider]:
    return [
        GeminiProvider(settings.gemini_api_key, settings.gemini_model),
        GroqProvider(settings.groq_api_key, settings.groq_model),
        OpenRouterProvider(settings.openrouter_api_key, settings.openrouter_model),
        OllamaProvider(settings.ollama_model, settings.ollama_host),
    ]


def available_providers() -> list[str]:
    """Nombres de los proveedores listos para usar (para mostrar en la UI)."""
    return [p.name for p in _all_providers() if p.is_available()]


class LLMRouter:
    """Prueba los proveedores disponibles en orden y devuelve la primera respuesta."""

    def __init__(self, providers: list[LLMProvider] | None = None):
        self.providers = providers or _all_providers()

    def has_any(self) -> bool:
        return any(p.is_available() for p in self.providers)

    def generate(self, system: str, prompt: str, temperature: float = 0.4) -> tuple[str, str]:
        """Devuelve (texto, nombre_del_proveedor_usado)."""
        errors: list[str] = []
        for provider in self.providers:
            if not provider.is_available():
                continue
            for attempt in range(3):  # hasta 3 intentos por proveedor
                try:
                    text = provider.generate(system, prompt, temperature)
                    if text:
                        return text, provider.name
                    break  # respuesta vacia: pasa al siguiente proveedor
                except Exception as exc:  # noqa: BLE001
                    msg = str(exc)
                    if _is_transient(msg) and attempt < 2:
                        time.sleep(5 * (attempt + 1))  # espera 5s, luego 10s
                        continue
                    errors.append(f"{provider.name}: {exc}")
                    break
        if not errors:
            raise LLMError(
                "No hay ninguna IA configurada. Pon una clave gratuita en el archivo .env "
                "(Gemini o Groq) o instala Ollama."
            )
        raise LLMError("Todas las IAs fallaron:\n- " + "\n- ".join(errors))

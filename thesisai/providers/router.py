"""Enrutador de IAs gratuitas: intenta varias en orden hasta que una responda.

Orden de preferencia: Gemini -> Groq -> Ollama.
Asi, si una gratuita se queda sin cupo, el bot continua con otra.
"""
from __future__ import annotations

from ..config import settings
from .base import LLMProvider
from .gemini import GeminiProvider
from .groq import GroqProvider
from .ollama import OllamaProvider


class LLMError(RuntimeError):
    """Ningun proveedor de IA pudo responder."""


def _all_providers() -> list[LLMProvider]:
    return [
        GeminiProvider(settings.gemini_api_key, settings.gemini_model),
        GroqProvider(settings.groq_api_key, settings.groq_model),
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
            try:
                text = provider.generate(system, prompt, temperature)
                if text:
                    return text, provider.name
            except Exception as exc:  # noqa: BLE001 - probamos el siguiente
                errors.append(f"{provider.name}: {exc}")
        if not errors:
            raise LLMError(
                "No hay ninguna IA configurada. Pon una clave gratuita en el archivo .env "
                "(Gemini o Groq) o instala Ollama."
            )
        raise LLMError("Todas las IAs fallaron:\n- " + "\n- ".join(errors))

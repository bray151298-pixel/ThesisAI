"""Interfaz comun para los proveedores de IA (LLM)."""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def is_available(self) -> bool:
        """True si el proveedor tiene clave/host configurado."""

    @abstractmethod
    def generate(self, system: str, prompt: str, temperature: float = 0.4) -> str:
        """Devuelve el texto generado o lanza una excepcion."""

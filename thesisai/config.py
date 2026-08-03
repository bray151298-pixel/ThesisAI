"""Carga de configuracion desde variables de entorno (.env)."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# En Streamlit Cloud no hay .env: las claves se cargan desde "Secrets".
# Streamlit las expone en st.secrets; las volcamos a variables de entorno
# para que el resto del codigo funcione igual en local y en la nube.
try:  # pragma: no cover - solo aplica dentro de Streamlit
    import streamlit as _st

    for _k, _v in _st.secrets.items():
        os.environ.setdefault(_k, str(_v))
except Exception:
    pass


def _clean(value: str | None) -> str:
    return (value or "").strip()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = _clean(os.getenv("GEMINI_API_KEY"))
    gemini_model: str = _clean(os.getenv("GEMINI_MODEL")) or "gemini-flash-latest"

    groq_api_key: str = _clean(os.getenv("GROQ_API_KEY"))
    groq_model: str = _clean(os.getenv("GROQ_MODEL")) or "llama-3.3-70b-versatile"

    ollama_model: str = _clean(os.getenv("OLLAMA_MODEL")) or "llama3.1"
    ollama_host: str = _clean(os.getenv("OLLAMA_HOST")) or "http://localhost:11434"

    # CORE (core.ac.uk) - agregador de repositorios (muchas tesis). Clave gratis.
    core_api_key: str = _clean(os.getenv("CORE_API_KEY"))

    # Contrasena para proteger la app cuando este publicada (vacia = sin login, uso local).
    app_password: str = _clean(os.getenv("APP_PASSWORD"))

    contact_email: str = _clean(os.getenv("CONTACT_EMAIL")) or "anonymous@example.com"


settings = Settings()

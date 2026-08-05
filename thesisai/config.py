"""Carga de configuracion desde variables de entorno (.env) o Streamlit Secrets."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _from_secrets(key: str) -> str | None:
    """Lee una clave desde st.secrets si estamos dentro de Streamlit Cloud."""
    try:  # pragma: no cover - solo aplica dentro de Streamlit
        import streamlit as st

        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        return None
    return None


def _get(key: str, default: str = "") -> str:
    """Prioriza variable de entorno (.env local); si no, usa Streamlit Secrets."""
    val = os.getenv(key)
    if val and val.strip():
        return val.strip()
    sec = _from_secrets(key)
    if sec and sec.strip():
        return sec.strip()
    return default


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = _get("GEMINI_API_KEY")
    gemini_model: str = _get("GEMINI_MODEL", "gemini-flash-latest")

    groq_api_key: str = _get("GROQ_API_KEY")
    groq_model: str = _get("GROQ_MODEL", "llama-3.3-70b-versatile")

    ollama_model: str = _get("OLLAMA_MODEL", "llama3.1")
    ollama_host: str = _get("OLLAMA_HOST", "http://localhost:11434")

    # CORE (core.ac.uk) - agregador de repositorios (muchas tesis). Clave gratis.
    core_api_key: str = _get("CORE_API_KEY")

    # Contrasena para proteger la app cuando este publicada (vacia = sin login).
    app_password: str = _get("APP_PASSWORD")

    contact_email: str = _get("CONTACT_EMAIL", "anonymous@example.com")


settings = Settings()

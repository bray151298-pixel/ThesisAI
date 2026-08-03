"""Busqueda en CORE (core.ac.uk) v3 - agregador de repositorios (muchas tesis).

Requiere una clave gratuita: https://core.ac.uk/services/api
Si no hay clave, este modulo simplemente no se usa.
"""
from __future__ import annotations

import requests

from ..config import settings
from .models import Article

API = "https://api.core.ac.uk/v3/search/works"


def is_enabled() -> bool:
    return bool(settings.core_api_key)


def _authors(items: list) -> list[str]:
    names = []
    for a in items or []:
        if isinstance(a, dict):
            name = a.get("name")
        else:
            name = str(a)
        if name:
            names.append(name)
    return names


def _url(w: dict) -> str:
    if w.get("downloadUrl"):
        return w["downloadUrl"]
    urls = w.get("sourceFulltextUrls") or []
    if urls:
        return urls[0]
    links = w.get("links") or []
    for ln in links:
        if isinstance(ln, dict) and ln.get("url"):
            return ln["url"]
    return ""


def _short_query(query: str, max_words: int = 4) -> str:
    """CORE une las palabras con AND; con muchas da 0 resultados.
    Nos quedamos con las primeras palabras clave (las mas importantes).
    """
    words = query.split()
    return " ".join(words[:max_words])


def search(
    query: str,
    year_from: int | None = None,
    year_to: int | None = None,
    doc_type: str = "",  # CORE no expone el tipo de forma fiable; se ignora en el filtro
    limit: int = 20,
) -> list[Article]:
    if not is_enabled():
        return []

    # Solo texto (corto) + rango de anios. El filtro documentType rompe la API.
    q_parts = [_short_query(query)]
    if year_from:
        q_parts.append(f"yearPublished>={year_from}")
    if year_to:
        q_parts.append(f"yearPublished<={year_to}")
    q = " AND ".join(q_parts)

    resp = requests.post(
        API,
        headers={"Authorization": f"Bearer {settings.core_api_key}"},
        json={"q": q, "limit": min(limit, 50)},
        timeout=40,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])

    articles: list[Article] = []
    for w in results:
        articles.append(
            Article(
                title=w.get("title") or "(sin titulo)",
                authors=_authors(w.get("authors", [])),
                year=w.get("yearPublished"),
                abstract=(w.get("abstract") or "").strip(),
                doi=w.get("doi") or "",
                url=_url(w),
                venue=w.get("publisher") or "",
                citations=w.get("citationCount") or 0,
                is_open_access=True,  # CORE agrega solo acceso abierto
                source="core",
                doc_type=(w.get("documentType") or "").lower(),
            )
        )
    return articles

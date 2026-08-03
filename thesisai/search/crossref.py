"""Busqueda en Crossref (gratis, sin clave). https://api.crossref.org"""
from __future__ import annotations

import requests

from ..config import settings
from .models import Article

API = "https://api.crossref.org/works"


def _authors(items: list[dict]) -> list[str]:
    names = []
    for a in items or []:
        given = a.get("given", "")
        family = a.get("family", "")
        full = f"{given} {family}".strip()
        if full:
            names.append(full)
    return names


def _year(item: dict) -> int | None:
    for key in ("published-print", "published-online", "issued", "created"):
        parts = (item.get(key) or {}).get("date-parts") or [[]]
        if parts and parts[0] and parts[0][0]:
            return parts[0][0]
    return None


def search(
    query: str,
    year_from: int | None = None,
    year_to: int | None = None,
    doc_type: str = "",
    limit: int = 20,
) -> list[Article]:
    params = {
        "query": query,
        "rows": min(limit, 50),
        "select": "DOI,title,author,container-title,issued,abstract,type,"
        "is-referenced-by-count,URL,published-print,published-online",
        "mailto": settings.contact_email,
    }
    filters = []
    if year_from:
        filters.append(f"from-pub-date:{year_from}-01-01")
    if year_to:
        filters.append(f"until-pub-date:{year_to}-12-31")
    if doc_type:
        filters.append(f"type:{doc_type}")
    if filters:
        params["filter"] = ",".join(filters)

    resp = requests.get(API, params=params, timeout=30)
    resp.raise_for_status()
    items = resp.json().get("message", {}).get("items", [])

    articles: list[Article] = []
    for it in items:
        title_list = it.get("title") or ["(sin titulo)"]
        venue_list = it.get("container-title") or [""]
        abstract = it.get("abstract", "")
        # Crossref envuelve el abstract en etiquetas JATS; limpieza minima.
        abstract = (
            abstract.replace("<jats:p>", "").replace("</jats:p>", "")
            .replace("<jats:title>", "").replace("</jats:title>", "")
        )
        articles.append(
            Article(
                title=title_list[0],
                authors=_authors(it.get("author", [])),
                year=_year(it),
                abstract=abstract.strip(),
                doi=it.get("DOI", ""),
                url=it.get("URL", ""),
                venue=venue_list[0] if venue_list else "",
                citations=it.get("is-referenced-by-count", 0),
                is_open_access=False,
                source="crossref",
                doc_type=it.get("type", ""),
            )
        )
    return articles

"""Busqueda en OpenAlex (gratis, sin clave). https://api.openalex.org"""
from __future__ import annotations

import requests

from ..config import settings
from .models import Article

API = "https://api.openalex.org/works"


def _abstract_from_index(inv: dict | None) -> str:
    """OpenAlex entrega el abstract como indice invertido; lo reconstruimos."""
    if not inv:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inv.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(word for _, word in positions)


def _authors(authorships: list[dict]) -> list[str]:
    names = []
    for a in authorships:
        author = a.get("author") or {}
        name = author.get("display_name")
        if name:
            names.append(name)
    return names


def search(
    query: str,
    year_from: int | None = None,
    year_to: int | None = None,
    open_access_only: bool = False,
    author: str = "",
    doc_type: str = "",
    sort: str = "relevance",
    limit: int = 20,
) -> list[Article]:
    filters = []
    if year_from:
        filters.append(f"from_publication_date:{year_from}-01-01")
    if year_to:
        filters.append(f"to_publication_date:{year_to}-12-31")
    if open_access_only:
        filters.append("is_oa:true")
    if author:
        filters.append(f"raw_author_name.search:{author}")
    if doc_type:
        filters.append(f"type:{doc_type}")

    params = {
        "search": query,
        "per_page": min(limit, 50),
        "mailto": settings.contact_email,
    }
    if filters:
        params["filter"] = ",".join(filters)
    if sort == "date":
        params["sort"] = "publication_date:desc"
    elif sort == "citations":
        params["sort"] = "cited_by_count:desc"

    resp = requests.get(API, params=params, timeout=30)
    resp.raise_for_status()
    results = resp.json().get("results", [])

    articles: list[Article] = []
    for w in results:
        loc = w.get("primary_location") or {}
        src = loc.get("source") or {}
        articles.append(
            Article(
                title=w.get("title") or "(sin titulo)",
                authors=_authors(w.get("authorships", [])),
                year=w.get("publication_year"),
                abstract=_abstract_from_index(w.get("abstract_inverted_index")),
                doi=(w.get("doi") or "").replace("https://doi.org/", ""),
                url=w.get("id", ""),
                venue=src.get("display_name") or "",
                citations=w.get("cited_by_count", 0),
                is_open_access=(w.get("open_access") or {}).get("is_oa", False),
                source="openalex",
                doc_type=w.get("type") or "",
            )
        )
    return articles

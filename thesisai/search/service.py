"""Servicio de busqueda avanzada: combina OpenAlex + Crossref y deduplica."""
from __future__ import annotations

from . import core_api, crossref, openalex
from .models import Article

# Traduce la eleccion del usuario al 'type' de cada base.
# clave -> (tipo_openalex, tipo_crossref, tipo_core)
DOC_TYPES = {
    "todos": ("", "", ""),
    "articulos": ("article", "journal-article", "research"),
    "tesis": ("dissertation", "dissertation", "thesis"),
    "libros": ("book", "book", "book"),
}


# Palabras vacias del espanol que no aportan a la busqueda.
_STOPWORDS = {
    "de", "del", "la", "las", "el", "los", "un", "una", "unos", "unas",
    "y", "o", "u", "e", "en", "a", "ante", "con", "por", "para", "segun",
    "sobre", "entre", "que", "cual", "como", "su", "sus", "al", "lo",
    "es", "son", "the", "of", "and", "in", "on", "for",
}


def clean_query(query: str) -> str:
    """Quita palabras vacias y espacios extra para mejorar la relevancia."""
    tokens = [t for t in query.split() if t.strip()]
    kept = [t for t in tokens if t.lower().strip(".,;:") not in _STOPWORDS]
    # Si al limpiar queda muy poco, conserva el original.
    return " ".join(kept) if len(kept) >= 2 else query.strip()


def _dedup(articles: list[Article]) -> list[Article]:
    seen: dict[str, Article] = {}
    for a in articles:
        k = (a.doi or a.title).lower().strip()
        if k not in seen:
            seen[k] = a
    return list(seen.values())


def _interleave(buckets: list[list[Article]]) -> list[Article]:
    """Mezcla las fuentes en ronda (1 de cada una) para que todas aparezcan."""
    from itertools import zip_longest

    mixed: list[Article] = []
    for group in zip_longest(*buckets):
        for a in group:
            if a is not None:
                mixed.append(a)
    return mixed


def search_articles(
    query: str,
    year_from: int | None = None,
    year_to: int | None = None,
    open_access_only: bool = False,
    author: str = "",
    doc_type: str = "todos",
    min_citations: int = 0,
    sort: str = "relevance",
    limit: int = 20,
    use_crossref: bool = True,
) -> list[Article]:
    """Busqueda unificada con filtros avanzados.

    - query: tema o palabras clave
    - year_from / year_to: rango de anios
    - open_access_only: solo articulos de acceso abierto
    - author: filtra por autor
    - min_citations: minimo de citas recibidas
    - sort: relevance | date | citations
    """
    query = clean_query((query or "").strip())
    if not query:
        return []

    oa_type, cr_type, core_type = DOC_TYPES.get(doc_type, ("", "", ""))

    buckets: list[list[Article]] = []
    try:
        buckets.append(openalex.search(
            query,
            year_from=year_from,
            year_to=year_to,
            open_access_only=open_access_only,
            author=author,
            doc_type=oa_type,
            sort=sort,
            limit=limit,
        ))
    except Exception:  # noqa: BLE001 - si una fuente falla, seguimos con la otra
        pass

    if use_crossref:
        try:
            buckets.append(crossref.search(
                query, year_from=year_from, year_to=year_to,
                doc_type=cr_type, limit=limit
            ))
        except Exception:  # noqa: BLE001
            pass

    # CORE: solo si hay clave configurada (muchas tesis de repositorios).
    if core_api.is_enabled():
        try:
            buckets.append(core_api.search(
                query, year_from=year_from, year_to=year_to,
                doc_type=core_type, limit=limit
            ))
        except Exception:  # noqa: BLE001
            pass

    results = _dedup(_interleave(buckets))

    if min_citations > 0:
        results = [a for a in results if a.citations >= min_citations]

    if sort == "date":
        results.sort(key=lambda a: a.year or 0, reverse=True)
    elif sort == "citations":
        results.sort(key=lambda a: a.citations, reverse=True)

    return results[:limit]

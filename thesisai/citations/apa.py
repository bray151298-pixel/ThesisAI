"""Generacion de referencias en formato APA 7 a partir de los articulos."""
from __future__ import annotations

from ..search.models import Article


def _format_authors_apa(authors: list[str]) -> str:
    """Apellido, N. N. — estilo APA. Ej: 'Perez, J., & Gomez, M.'."""
    if not authors:
        return "Autor desconocido"

    formatted = []
    for full in authors:
        parts = full.split()
        if len(parts) == 1:
            formatted.append(parts[0])
            continue
        family = parts[-1]
        initials = " ".join(f"{p[0].upper()}." for p in parts[:-1] if p)
        formatted.append(f"{family}, {initials}")

    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) <= 20:
        return ", ".join(formatted[:-1]) + ", & " + formatted[-1]
    # APA: 21+ autores -> primeros 19, puntos suspensivos, ultimo.
    return ", ".join(formatted[:19]) + ", ... " + formatted[-1]


def format_reference(a: Article) -> str:
    """Una referencia APA 7 para la lista bibliografica."""
    authors = _format_authors_apa(a.authors)
    year = a.year if a.year else "s.f."
    title = a.title.rstrip(".")
    parts = [f"{authors} ({year}). {title}."]
    if a.venue:
        parts.append(f"*{a.venue}*.")
    if a.doi:
        parts.append(f"https://doi.org/{a.doi}")
    elif a.url:
        parts.append(a.url)
    return " ".join(parts)


def build_bibliography(articles: list[Article]) -> list[str]:
    """Lista de referencias APA ordenada alfabeticamente."""
    refs = [format_reference(a) for a in articles]
    refs.sort(key=lambda s: s.lower())
    return refs

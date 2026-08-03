"""Modelo unificado de articulo academico."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Article:
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    abstract: str = ""
    doi: str = ""
    url: str = ""
    venue: str = ""            # revista / fuente
    citations: int = 0
    is_open_access: bool = False
    source: str = ""           # openalex | crossref
    doc_type: str = ""         # article | dissertation | book | ...

    @property
    def type_label(self) -> str:
        """Etiqueta legible del tipo de documento."""
        mapping = {
            "article": "Articulo",
            "journal-article": "Articulo",
            "dissertation": "Tesis",
            "thesis": "Tesis",
            "book": "Libro",
            "book-chapter": "Capitulo de libro",
            "proceedings-article": "Ponencia",
            "posted-content": "Preprint",
            "preprint": "Preprint",
            "report": "Informe",
        }
        return mapping.get(self.doc_type, self.doc_type or "Documento")

    @property
    def author_short(self) -> str:
        """Formato corto para cita en texto: 'Perez' o 'Perez y Gomez' o 'Perez et al.'."""
        if not self.authors:
            return "Autor desconocido"
        last_names = [a.split()[-1] for a in self.authors if a.strip()]
        if len(last_names) == 1:
            return last_names[0]
        if len(last_names) == 2:
            return f"{last_names[0]} y {last_names[1]}"
        return f"{last_names[0]} et al."

    @property
    def in_text_citation(self) -> str:
        year = self.year if self.year else "s.f."
        return f"({self.author_short}, {year})"

    @property
    def key(self) -> str:
        return self.doi or self.url or self.title

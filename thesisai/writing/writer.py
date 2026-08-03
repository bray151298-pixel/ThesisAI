"""Redactor asistido: genera borradores apoyados en los articulos seleccionados.

Regla clave: el modelo SOLO puede citar los articulos que se le entregan, y cada
afirmacion relevante debe llevar su cita en texto (Autor, Anio). Es un borrador que
el estudiante debe revisar y reescribir: la herramienta asiste, no reemplaza.
"""
from __future__ import annotations

from ..providers import LLMRouter
from ..search.models import Article

THESIS_SECTIONS = [
    "Resumen",
    "Introduccion",
    "Planteamiento del problema",
    "Objetivos",
    "Justificacion",
    "Marco teorico",
    "Antecedentes",
    "Metodologia",
    "Discusion",
    "Conclusiones",
]

SYSTEM = (
    "Eres un asistente de redaccion academica en espanol. Escribes con rigor, tono "
    "formal y estructura clara. REGLAS ESTRICTAS: (1) Solo puedes basarte en las "
    "fuentes que se te proporcionan; no inventes datos, autores ni citas. (2) Cada "
    "afirmacion que provenga de una fuente debe llevar su cita en texto en formato "
    "APA (Apellido, Anio), usando exactamente las citas indicadas. (3) Si la "
    "informacion disponible es insuficiente, dilo explicitamente en lugar de "
    "inventar. (4) Produces un BORRADOR que el investigador debe revisar."
)


def _sources_block(articles: list[Article]) -> str:
    lines = []
    for i, a in enumerate(articles, 1):
        abstract = (a.abstract or "").strip()
        if len(abstract) > 1200:
            abstract = abstract[:1200] + "..."
        lines.append(
            f"[Fuente {i}] Cita en texto: {a.in_text_citation}\n"
            f"Titulo: {a.title}\n"
            f"Autores: {', '.join(a.authors) or 'desconocido'} | Anio: {a.year or 's.f.'}\n"
            f"Revista: {a.venue or 'n/d'}\n"
            f"Resumen: {abstract or '(sin resumen disponible)'}\n"
        )
    return "\n".join(lines)


def draft_section(
    topic: str,
    section: str,
    articles: list[Article],
    extra_notes: str = "",
    router: LLMRouter | None = None,
) -> tuple[str, str]:
    """Genera el borrador de una seccion. Devuelve (texto, proveedor_usado)."""
    router = router or LLMRouter()
    sources = _sources_block(articles) if articles else "(No se seleccionaron fuentes.)"

    prompt = (
        f"TEMA DE LA TESIS: {topic}\n\n"
        f"SECCION A REDACTAR: {section}\n\n"
        f"FUENTES DISPONIBLES (usa solo estas para citar):\n{sources}\n\n"
        f"{('NOTAS DEL INVESTIGADOR: ' + extra_notes) if extra_notes else ''}\n\n"
        f"Redacta la seccion '{section}' de forma coherente y bien estructurada, "
        f"integrando y citando las fuentes anteriores con sus citas en texto (Autor, "
        f"Anio). No agregues una lista de referencias al final (se genera aparte). "
        f"Escribe en espanol academico."
    )
    return router.generate(SYSTEM, prompt, temperature=0.4)

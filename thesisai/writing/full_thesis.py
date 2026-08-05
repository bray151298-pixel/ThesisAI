"""Generador de una TESIS MODELO COMPLETA (plantilla guiada por fases).

Genera todas las secciones de una tesis siguiendo el flujo academico. Las
secciones empiricas (metodologia, recoleccion, resultados) incluyen datos de
EJEMPLO claramente etiquetados y notas de "lo que tu debes hacer en campo".
NO reemplaza la investigacion real del estudiante: es un modelo para completar.
"""
from __future__ import annotations

from ..providers import LLMRouter
from ..search.models import Article
from .writer import _sources_block

# Fases del proceso de tesis (para mostrar el mapa/roadmap en la interfaz).
THESIS_PHASES = [
    "Tema",
    "Buscar literatura",
    "Leer artículos",
    "Analizar investigaciones",
    "Encontrar el problema",
    "Formular objetivos",
    "Crear hipótesis",
    "Marco teórico",
    "Metodología",
    "Recolección de datos",
    "Análisis",
    "Resultados",
    "Discusión",
    "Conclusiones",
    "Referencias",
    "Exportar",
]

# Secciones que se redactan, en orden, con su tipo:
#   "teorica"  -> se apoya en las fuentes y cita (Autor, Anio)
#   "empirica" -> incluye datos de EJEMPLO etiquetados + notas de campo
FULL_THESIS_SECTIONS: list[tuple[str, str]] = [
    ("Resumen", "teorica"),
    ("Introduccion", "teorica"),
    ("Planteamiento del problema", "teorica"),
    ("Objetivos", "teorica"),
    ("Hipotesis", "teorica"),
    ("Justificacion", "teorica"),
    ("Antecedentes", "teorica"),
    ("Marco teorico", "teorica"),
    ("Metodologia", "empirica"),
    ("Recoleccion de datos", "empirica"),
    ("Resultados", "empirica"),
    ("Discusion", "teorica"),
    ("Conclusiones", "teorica"),
    ("Recomendaciones", "teorica"),
]

# Orden canonico completo (para ordenar el documento al exportar).
FULL_ORDER = [name for name, _ in FULL_THESIS_SECTIONS]

_SYSTEM_BASE = (
    "Eres un asistente de redaccion academica en espanol, con rigor y tono formal. "
    "Produces un BORRADOR MODELO que el investigador debe revisar, adaptar a su caso "
    "real y completar. REGLAS: (1) Para lo teorico, apoyate SOLO en las fuentes dadas "
    "y cita en texto en formato APA (Apellido, Anio) usando exactamente las citas "
    "indicadas; no inventes autores ni citas. (2) Estructura clara con subtitulos."
)

_EMPIRICA_EXTRA = (
    "\n\nESTA SECCION ES EMPIRICA (trabajo de campo). Como es una tesis MODELO de "
    "ejemplo:\n"
    "- Incluye datos estadisticos ILUSTRATIVOS (tablas de frecuencias, porcentajes, "
    "medias, o un coeficiente de correlacion de ejemplo) para mostrar el formato.\n"
    "- Marca SIEMPRE los datos inventados con la etiqueta literal: "
    "'⚠️ EJEMPLO — reemplaza con tus datos reales'.\n"
    "- Agrega uno o mas recuadros que empiecen con '📌 LO QUE TU DEBES HACER:' "
    "explicando el trabajo real (calcular la muestra con tu poblacion, aplicar el "
    "instrumento, tabular en Excel/SPSS, etc.).\n"
    "- NUNCA presentes los datos de ejemplo como si fueran resultados reales."
)


def phase_flow_markdown() -> str:
    """Devuelve el flujo de fases como texto con flechas (para la interfaz)."""
    return "  →  ".join(THESIS_PHASES)


def draft_full_section(
    topic: str,
    section: str,
    kind: str,
    articles: list[Article],
    router: LLMRouter | None = None,
) -> tuple[str, str]:
    """Redacta una seccion de la tesis modelo. Devuelve (texto, proveedor)."""
    router = router or LLMRouter()
    sources = _sources_block(articles) if articles else "(No se seleccionaron fuentes.)"
    system = _SYSTEM_BASE + (_EMPIRICA_EXTRA if kind == "empirica" else "")

    prompt = (
        f"TEMA DE LA TESIS: {topic}\n\n"
        f"SECCION A REDACTAR: {section}\n\n"
        f"FUENTES DISPONIBLES (usa solo estas para citar):\n{sources}\n\n"
        f"Redacta la seccion '{section}' de una tesis modelo, bien estructurada y en "
        f"espanol academico. No agregues la lista de referencias al final "
        f"(se genera aparte)."
    )
    return router.generate(system, prompt, temperature=0.45)

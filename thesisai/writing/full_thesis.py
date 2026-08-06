"""Generador de TESIS MODELO COMPLETA con la estructura oficial UNAJMA.

Estructuras basadas en el Anexo 02 (Escuela de Posgrado UNAJMA):
  - "proyecto": Capitulos I-IV (termina en Aspectos administrativos). Es la
    propuesta que se presenta ANTES del trabajo de campo (sin resultados).
  - "tesis_final": Cap I-III (UNAJMA) + Resultados + Discusion/Conclusiones,
    con datos de EJEMPLO etiquetados y notas de "lo que tu debes hacer".

Genera un capitulo por llamada (con sus subsecciones numeradas), para no
saturar la IA gratuita. Es un modelo para completar, no para entregar tal cual.
"""
from __future__ import annotations

from ..providers import LLMRouter
from ..search.models import Article
from .writer import _sources_block

# Fases del proceso (para el mapa/roadmap en la interfaz).
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

# Cada item: (titulo_capitulo, tipo, guia_de_subsecciones)
#   tipo "teorica"  -> se apoya en fuentes y cita (Autor, Anio)
#   tipo "empirica" -> incluye datos/tablas de EJEMPLO etiquetados + notas de campo

_CAP_PROBLEMA = (
    "CAPÍTULO I. EL PROBLEMA",
    "teorica",
    "Incluye estas subsecciones numeradas:\n"
    "1.1. Planteamiento del problema\n"
    "1.2. Formulación del problema (problema general y específicos, en forma de pregunta)\n"
    "1.3. Objetivos de la investigación (1.3.1. Objetivo general; 1.3.2. Objetivos específicos)\n"
    "1.4. Justificación e importancia",
)

_CAP_MARCO = (
    "CAPÍTULO II. MARCO TEÓRICO",
    "teorica",
    "Incluye estas subsecciones numeradas:\n"
    "2.1. Antecedentes de la investigación (resume y cita las fuentes dadas)\n"
    "2.2. Bases teóricas\n"
    "2.3. Definición de términos\n"
    "2.4. Formulación de hipótesis (general y específicas)\n"
    "2.5. Identificación de variables\n"
    "2.6. Definición operativa de variables e indicadores (tabla)",
)

_CAP_METODOLOGIA = (
    "CAPÍTULO III. METODOLOGÍA",
    "empirica",
    "Incluye estas subsecciones numeradas:\n"
    "3.1. Tipo de investigación\n"
    "3.2. Nivel de investigación\n"
    "3.3. Método de investigación\n"
    "3.4. Diseño de investigación\n"
    "3.5. Población, muestra y muestreo (incluye una fórmula de tamaño de muestra de EJEMPLO)\n"
    "3.6. Técnicas e instrumentos de recolección de datos\n"
    "3.7. Técnicas de procesamiento y análisis de datos\n"
    "3.8. Descripción de la prueba de hipótesis",
)

_MATRIZ = (
    "Matriz de consistencia",
    "empirica",
    "Presenta una TABLA de matriz de consistencia con columnas: "
    "Problema | Objetivos | Hipótesis | Variables | Metodología. "
    "Las filas deben estar alineadas (problema general con objetivo general, etc.).",
)

STRUCTURES: dict[str, list[tuple[str, str, str]]] = {
    "proyecto": [
        ("Resumen", "teorica",
         "Resumen de 200-250 palabras (problema, objetivo, metodología propuesta) "
         "y 3-5 palabras clave."),
        _CAP_PROBLEMA,
        _CAP_MARCO,
        _CAP_METODOLOGIA,
        ("CAPÍTULO IV. ASPECTOS ADMINISTRATIVOS", "empirica",
         "Incluye estas subsecciones numeradas:\n"
         "4.1. Potencial humano\n4.2. Materiales y equipos\n"
         "4.3. Cronograma de actividades (tabla de EJEMPLO por meses)\n"
         "4.4. Presupuesto (tabla de EJEMPLO con montos)\n4.5. Financiamiento"),
        _MATRIZ,
    ],
    "tesis_final": [
        ("Resumen", "teorica",
         "Resumen de 200-250 palabras (problema, objetivo, método, resultados "
         "principales, conclusión) y 3-5 palabras clave."),
        _CAP_PROBLEMA,
        _CAP_MARCO,
        _CAP_METODOLOGIA,
        ("CAPÍTULO IV. RESULTADOS", "empirica",
         "Incluye:\n4.1. Análisis descriptivo (tablas de frecuencias y porcentajes de EJEMPLO)\n"
         "4.2. Análisis inferencial / prueba de hipótesis "
         "(ej. coeficiente Rho de Spearman de EJEMPLO con su interpretación)"),
        ("CAPÍTULO V. DISCUSIÓN, CONCLUSIONES Y RECOMENDACIONES", "teorica",
         "Incluye:\n5.1. Discusión (contrasta tus resultados con los antecedentes citados)\n"
         "5.2. Conclusiones (una por cada objetivo)\n5.3. Recomendaciones"),
        _MATRIZ,
    ],
}

STRUCTURE_LABELS = {
    "proyecto": "Proyecto de tesis (UNAJMA, Cap. I–IV, sin resultados)",
    "tesis_final": "Tesis final completa (UNAJMA, con resultados de ejemplo)",
}


def chapters_for(structure: str) -> list[tuple[str, str, str]]:
    return STRUCTURES.get(structure, STRUCTURES["proyecto"])


def order_for(structure: str) -> list[str]:
    return [c[0] for c in chapters_for(structure)]


_SYSTEM_BASE = (
    "Eres un asistente de redaccion academica en espanol, con rigor y tono formal, "
    "que sigue la estructura de la Escuela de Posgrado de la UNAJMA. Produces un "
    "BORRADOR MODELO que el investigador debe revisar, adaptar a su caso real y "
    "completar. REGLAS: (1) Para lo teorico, apoyate SOLO en las fuentes dadas y "
    "cita en texto en formato APA (Apellido, Anio) usando exactamente las citas "
    "indicadas; no inventes autores ni citas. (2) Respeta EXACTAMENTE los titulos y "
    "la numeracion de subsecciones que se te indican."
)

_EMPIRICA_EXTRA = (
    "\n\nESTE CAPITULO INCLUYE PARTES EMPIRICAS / DE CAMPO. Como es una tesis MODELO:\n"
    "- Donde haya numeros, tablas o datos, usa datos ILUSTRATIVOS para mostrar el formato.\n"
    "- Marca SIEMPRE esos datos con la etiqueta literal: "
    "'⚠️ EJEMPLO — reemplaza con tus datos reales'.\n"
    "- Agrega recuadros que empiecen con '📌 LO QUE TU DEBES HACER:' explicando el "
    "trabajo real (calcular la muestra con tu poblacion, aplicar el instrumento, "
    "tabular en Excel/SPSS, etc.).\n"
    "- NUNCA presentes los datos de ejemplo como si fueran reales."
)


def phase_flow_markdown() -> str:
    return "  →  ".join(THESIS_PHASES)


def draft_chapter(
    topic: str,
    title: str,
    kind: str,
    guidance: str,
    articles: list[Article],
    router: LLMRouter | None = None,
) -> tuple[str, str]:
    """Redacta un capitulo completo (con sus subsecciones). Devuelve (texto, proveedor)."""
    router = router or LLMRouter()
    sources = _sources_block(articles) if articles else "(No se seleccionaron fuentes.)"
    system = _SYSTEM_BASE + (_EMPIRICA_EXTRA if kind == "empirica" else "")

    prompt = (
        f"TEMA DE LA TESIS: {topic}\n\n"
        f"SECCION/CAPITULO A REDACTAR: {title}\n\n"
        f"GUIA DE CONTENIDO Y SUBSECCIONES:\n{guidance}\n\n"
        f"FUENTES DISPONIBLES (usa solo estas para citar):\n{sources}\n\n"
        f"Redacta el capitulo completo en espanol academico, respetando los titulos y "
        f"la numeracion indicados. No agregues la lista de referencias al final "
        f"(se genera aparte)."
    )
    return router.generate(system, prompt, temperature=0.45)

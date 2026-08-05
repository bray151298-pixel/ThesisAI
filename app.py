"""ThesisAI - App principal (Streamlit).

Ejecutar con:  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from thesisai.config import settings
from thesisai.citations import build_bibliography
from thesisai.export import build_docx
from thesisai.providers import LLMRouter, LLMError, available_providers
from thesisai.search import search_articles
from thesisai.search import core_api
from thesisai.writing import (
    THESIS_SECTIONS,
    draft_section,
    THESIS_PHASES,
    FULL_THESIS_SECTIONS,
    FULL_ORDER,
    draft_full_section,
)

st.set_page_config(page_title="ThesisAI", page_icon="📚", layout="wide")


# ---- Login (solo si hay contrasena configurada) ----
def _check_password() -> bool:
    if not settings.app_password:
        return True  # sin contrasena => uso local, acceso libre
    if st.session_state.get("auth_ok"):
        return True

    st.title("📚 ThesisAI")
    st.caption("Acceso privado")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if pwd == settings.app_password:
            st.session_state["auth_ok"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    return False


if not _check_password():
    st.stop()


# ---- Estado de sesion ----
if "results" not in st.session_state:
    st.session_state.results = []          # articulos encontrados
if "selected" not in st.session_state:
    st.session_state.selected = {}         # key -> Article seleccionado
if "sections" not in st.session_state:
    st.session_state.sections = {}         # nombre_seccion -> texto redactado


# ---------------------------------------------------------------- Sidebar
with st.sidebar:
    st.title("📚 ThesisAI")
    st.caption("Asistente de investigacion con IA gratuita")

    provs = available_providers()
    if provs:
        st.success("IA lista: " + ", ".join(provs))
    else:
        st.warning(
            "No hay IA configurada. La busqueda funciona igual, pero para "
            "redactar pon una clave gratuita en el archivo **.env** "
            "(Gemini o Groq) o instala Ollama."
        )

    # --- Diagnostico temporal: ver si las claves llegan (solo si/no) ---
    with st.expander("🔧 Diagnóstico de claves"):
        import os as _os
        try:
            _secret_keys = list(st.secrets.keys())
        except Exception:
            _secret_keys = []
        st.caption(f"Claves en Secrets (nube): {len(_secret_keys)}")
        for _k in ["GEMINI_API_KEY", "GROQ_API_KEY", "CORE_API_KEY", "APP_PASSWORD"]:
            _in_env = bool((_os.getenv(_k) or "").strip())
            _in_sec = _k in _secret_keys
            st.write(f"- `{_k}`: env={_in_env} · secrets={_in_sec}")
        st.caption(f"gemini_api_key cargada: {bool(settings.gemini_api_key)}")

    st.divider()
    st.metric("Fuentes seleccionadas", len(st.session_state.selected))
    st.metric("Secciones redactadas", len(st.session_state.sections))
    if st.session_state.selected:
        if st.button("Limpiar seleccion", use_container_width=True):
            st.session_state.selected = {}
            st.rerun()


tab_search, tab_write, tab_full, tab_export = st.tabs(
    ["🔎 Buscar articulos", "✍️ Redactar", "🎓 Tesis completa", "📄 Exportar"]
)


# ---------------------------------------------------------------- Buscar
with tab_search:
    st.subheader("Buscador avanzado de articulos academicos")
    _fuentes = "OpenAlex + Crossref"
    if core_api.is_enabled():
        _fuentes += " + CORE (tesis de repositorios)"
    else:
        _fuentes += " · (activa CORE con su clave para mas tesis)"
    st.caption(f"Fuentes: {_fuentes} — gratis.")

    with st.expander("❓ ¿Cómo lleno el buscador? (guía rápida)"):
        st.markdown(
            "- **Tema:** escribe 3-6 palabras clave, NO el título completo. "
            "Ej: `motivación laboral y desempeño en enfermeras`.\n"
            "- Evita siglas locales y errores de ortografía.\n"
            "- **Tipo:** elige **Tesis** para ver solo tesis.\n"
            "- Pasa el mouse por el **ⓘ** de cada campo para ver un ejemplo."
        )

    with st.form("search_form"):
        query = st.text_input(
            "Tema o palabras clave",
            placeholder="ej. calidad servicio educativo satisfaccion estudiantes",
            help="Escribe 3-6 palabras clave del tema (no el título completo). "
            "Ejemplo: `satisfacción estudiantil educación técnica`. "
            "Evita siglas locales como CEPRO/CETPRO.",
        )
        c1, c2, c3 = st.columns(3)
        year_from = c1.number_input(
            "Desde (anio)", min_value=1900, max_value=2100, value=2018,
            help="Año más antiguo a incluir. Ejemplo: 2018 = solo desde 2018 en adelante.",
        )
        year_to = c2.number_input(
            "Hasta (anio)", min_value=1900, max_value=2100, value=2026,
            help="Año más reciente a incluir. Ejemplo: 2026 = hasta este año.",
        )
        limit = c3.number_input(
            "Resultados", min_value=5, max_value=50, value=20,
            help="Cuántos resultados mostrar. Ejemplo: 20. Más = búsqueda un poco más lenta.",
        )

        c4, c5, c6 = st.columns(3)
        author = c4.text_input(
            "Autor (opcional)",
            help="Filtra por apellido del autor. Ejemplo: `Chiroque`. Déjalo vacío para no filtrar.",
        )
        min_citations = c5.number_input(
            "Min. citas", min_value=0, value=0,
            help="Solo trabajos con al menos estas citas. Ejemplo: 5 = descarta los poco citados. "
            "0 = no filtra (las tesis suelen tener pocas citas).",
        )
        sort = c6.selectbox(
            "Ordenar por", ["relevance", "citations", "date"],
            format_func=lambda s: {"relevance": "Relevancia", "citations": "Mas citados", "date": "Mas recientes"}[s],
            help="Relevancia = más parecidos al tema (recomendado). "
            "Más citados = más influyentes. Más recientes = por año.",
        )

        c7, c8 = st.columns(2)
        doc_type = c7.selectbox(
            "Tipo de documento",
            ["todos", "articulos", "tesis", "libros"],
            format_func=lambda s: {"todos": "Todos", "articulos": "Articulos", "tesis": "Tesis", "libros": "Libros"}[s],
            help="Filtra por tipo. Ejemplo: **Tesis** = solo tesis/disertaciones. "
            "**Todos** = máxima cobertura (artículos + tesis + libros).",
        )
        open_access_only = c8.checkbox(
            "Solo acceso abierto (PDF disponible)",
            help="Márcalo para ver solo trabajos con PDF gratis descargable. "
            "Útil si necesitas leer el texto completo.",
        )

        submitted = st.form_submit_button(
            "Buscar", type="primary",
            help="Busca en OpenAlex + Crossref + CORE con los filtros de arriba.",
        )

    if submitted:
        with st.spinner("Buscando en bases academicas..."):
            st.session_state.results = search_articles(
                query,
                year_from=int(year_from),
                year_to=int(year_to),
                open_access_only=open_access_only,
                author=author,
                doc_type=doc_type,
                min_citations=int(min_citations),
                sort=sort,
                limit=int(limit),
            )
        n = len(st.session_state.results)
        if n:
            st.success(f"{n} resultados encontrados.")
        else:
            st.warning("No se encontraron resultados con esos filtros.")
            # Intenta ampliar automaticamente a 'Todos' para ayudar al usuario.
            broadened = []
            if doc_type != "todos":
                broadened = search_articles(
                    query, year_from=int(year_from), year_to=int(year_to),
                    doc_type="todos", limit=int(limit),
                )
            tips = [
                "Usa **3-6 palabras clave** en vez del titulo completo.",
                "Evita siglas locales (ej. *CEPROS*) y revisa la ortografia.",
                "Amplia el rango de años o quita el filtro de tipo/acceso abierto.",
            ]
            st.info("💡 Sugerencias:\n\n- " + "\n- ".join(tips))
            if broadened:
                st.write(
                    f"🔎 Con el tipo **Todos** sí hay **{len(broadened)}** resultados para ese tema:"
                )
                if st.button(f"Mostrar los {len(broadened)} resultados (Todos)"):
                    st.session_state.results = broadened
                    st.rerun()

    for i, art in enumerate(st.session_state.results):
        with st.container(border=True):
            top = st.columns([0.08, 0.92])
            checked = art.key in st.session_state.selected
            if top[0].checkbox("Usar", value=checked, key=f"chk_{i}", label_visibility="collapsed"):
                st.session_state.selected[art.key] = art
            else:
                st.session_state.selected.pop(art.key, None)

            with top[1]:
                type_icon = "🎓" if art.type_label == "Tesis" else "📄"
                st.markdown(f"{type_icon} **{art.title}**")
                meta = f"`{art.type_label}` · {art.author_short} · {art.year or 's.f.'} · {art.venue or 's/revista'}"
                meta += f" · 🔖 {art.citations} citas"
                if art.is_open_access:
                    meta += " · 🟢 Acceso abierto"
                src_label = {"openalex": "OpenAlex", "crossref": "Crossref", "core": "📚 CORE (repositorio)"}
                meta += f" · {src_label.get(art.source, art.source)}"
                st.caption(meta)
                if art.abstract:
                    st.write(art.abstract[:400] + ("..." if len(art.abstract) > 400 else ""))
                if art.url:
                    st.markdown(f"[Ver fuente]({art.url})")


# ---------------------------------------------------------------- Redactar
with tab_write:
    st.subheader("Redactar seccion de la tesis")
    selected = list(st.session_state.selected.values())

    if not selected:
        st.info("Primero busca y selecciona articulos en la pestana **Buscar**.")
    else:
        st.caption(f"Se redactara usando {len(selected)} fuentes seleccionadas, con citas (Autor, Anio).")
        topic = st.text_input(
            "Tema / titulo de la tesis", key="topic",
            help="El título real de tu tesis. Ejemplo: `Calidad del servicio educativo y "
            "satisfacción de los estudiantes en CETPROs de Andahuaylas, 2026`.",
        )
        section = st.selectbox(
            "Seccion a redactar", THESIS_SECTIONS,
            help="Elige qué parte redactar. Ejemplo: **Introducción** primero, luego "
            "**Marco teórico**, etc. Cada sección se guarda por separado.",
        )
        notes = st.text_area(
            "Notas o instrucciones para esta seccion (opcional)",
            help="Indicaciones extra para la IA. Ejemplo: `Enfócate en el contexto peruano y "
            "usa un tono formal` o `menciona las dimensiones de la variable calidad`.",
        )

        if st.button("Generar borrador", type="primary"):
            if not LLMRouter().has_any():
                st.error("No hay IA configurada. Pon una clave gratuita en el archivo .env.")
            elif not topic.strip():
                st.warning("Escribe el tema de la tesis.")
            else:
                with st.spinner("Redactando con IA..."):
                    try:
                        text, used = draft_section(topic, section, selected, extra_notes=notes)
                        st.session_state.sections[section] = text
                        st.success(f"Borrador generado con: {used}")
                    except LLMError as e:
                        st.error(str(e))

        if section in st.session_state.sections:
            st.divider()
            edited = st.text_area(
                f"Borrador de '{section}' (editable)",
                value=st.session_state.sections[section],
                height=400,
            )
            st.session_state.sections[section] = edited
            st.caption("⚠️ Es un borrador asistido: revisa, verifica las citas y reescribe con tus palabras.")


# ---------------------------------------------------------------- Tesis completa
with tab_full:
    st.subheader("🎓 Generar tesis modelo completa")
    st.caption(
        "Genera TODAS las secciones de una tesis siguiendo las fases académicas. "
        "Las partes de campo traen datos de **ejemplo** (etiquetados) y notas de "
        "**lo que tú debes hacer**. Es un modelo para completar, no para entregar tal cual."
    )

    # Mapa visual de fases
    with st.expander("🗺️ Fases de la tesis (así trabaja el bot)", expanded=True):
        _cols = st.columns(4)
        for _i, _ph in enumerate(THESIS_PHASES):
            _cols[_i % 4].markdown(f"**{_i + 1}.** {_ph}")

    selected_full = list(st.session_state.selected.values())
    if not selected_full:
        st.info(
            "Primero busca y selecciona algunos artículos en **🔎 Buscar** "
            "(4-6 fuentes bastan). Se usarán para el marco teórico y las citas."
        )
    else:
        st.success(f"{len(selected_full)} fuentes seleccionadas para citar.")

    topic_full = st.text_input(
        "Título / tema de tu tesis",
        key="topic",
        help="Ejemplo: Calidad del servicio educativo y satisfacción de los "
        "estudiantes en CETPROs de Andahuaylas, 2026.",
    )

    st.warning(
        "⚠️ **Uso responsable:** los datos estadísticos que genere son EJEMPLOS "
        "ilustrativos. Debes reemplazarlos con los resultados reales de tu trabajo "
        "de campo. Entregar datos inventados como reales es deshonestidad académica."
    )

    _n_sec = len(FULL_THESIS_SECTIONS)
    if st.button(f"🚀 Generar tesis modelo completa ({_n_sec} secciones)", type="primary"):
        if not LLMRouter().has_any():
            st.error("No hay IA configurada.")
        elif not topic_full.strip():
            st.warning("Escribe el título/tema de tu tesis.")
        elif not selected_full:
            st.warning("Selecciona al menos una fuente en la pestaña Buscar.")
        else:
            progress = st.progress(0.0, text="Preparando...")
            done, errors = 0, []
            for idx, (sec_name, sec_kind) in enumerate(FULL_THESIS_SECTIONS):
                progress.progress(
                    idx / _n_sec, text=f"Redactando: {sec_name} ({idx + 1}/{_n_sec})"
                )
                try:
                    text, _used = draft_full_section(
                        topic_full, sec_name, sec_kind, selected_full
                    )
                    st.session_state.sections[sec_name] = text
                    done += 1
                except LLMError as e:
                    errors.append(f"{sec_name}: {e}")
            progress.progress(1.0, text="¡Listo!")
            if done:
                st.success(
                    f"✅ Se generaron {done}/{_n_sec} secciones. "
                    "Revísalas en **✍️ Redactar** y descárgalas en **📄 Exportar**."
                )
            if errors:
                st.error(
                    "Algunas secciones fallaron (probable límite de la IA gratis; "
                    "espera un momento y reintenta):\n\n- " + "\n- ".join(errors[:5])
                )

    if st.session_state.sections:
        st.divider()
        st.caption("Secciones ya generadas (edítalas en ✍️ Redactar):")
        for _name in FULL_ORDER:
            if _name in st.session_state.sections:
                st.markdown(f"✅ {_name}")


# ---------------------------------------------------------------- Exportar
with tab_export:
    st.subheader("Exportar tesis a Word")
    if not st.session_state.sections:
        st.info("Aun no hay secciones redactadas. Ve a la pestana **Redactar**.")
    else:
        title = st.text_input("Titulo del documento", value=st.session_state.get("topic", "Tesis"))
        author_name = st.text_input("Autor(a)")

        st.write("Secciones incluidas:")
        for name in st.session_state.sections:
            st.write(f"• {name}")

        selected = list(st.session_state.selected.values())
        refs = build_bibliography(selected)
        st.write(f"Referencias (APA 7): **{len(refs)}**")
        with st.expander("Ver referencias"):
            for r in refs:
                st.markdown(f"- {r}")

        # Ordena las secciones segun el orden canonico completo de una tesis
        _canonical = FULL_ORDER + [n for n in st.session_state.sections if n not in FULL_ORDER]
        ordered = [(n, st.session_state.sections[n]) for n in _canonical if n in st.session_state.sections]

        docx_bytes = build_docx(title, author_name, ordered, refs)
        st.download_button(
            "⬇️ Descargar .docx",
            data=docx_bytes,
            file_name="tesis_thesisai.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
        )

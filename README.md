# 📚 ThesisAI — Fase 1

Asistente de investigación con **IA gratuita** que:

1. **Busca artículos académicos** (buscador avanzado sobre OpenAlex + Crossref — gratis, sin clave).
2. **Redacta borradores** de tu tesis apoyándose en esos artículos, **con citas (Autor, Año)**.
3. **Exporta a Word (.docx)** con referencias en formato **APA 7**.

> Es un asistente: genera **borradores** que tú debes revisar, verificar y reescribir.
> Las IAs se combinan automáticamente: **Gemini → Groq → Ollama** (usa la que tengas).

---

## 🚀 Cómo usarlo (Windows)

### 1. Instalar dependencias
```bash
cd /d D:\ThesisAI
python -m pip install -r requirements.txt
```

### 2. Configurar una IA gratis (opcional para buscar, necesario para redactar)
Copia `.env.example` como `.env` y pon **al menos una** clave gratuita:

- **Gemini** (recomendado): consigue tu clave gratis en https://aistudio.google.com/app/apikey
- **Groq** (gratis, rápido): https://console.groq.com/keys
- **Ollama** (offline): instala https://ollama.com y ejecuta `ollama pull llama3.1`

```bash
copy .env.example .env
```
…y edita `.env` con tu clave.

### 3. Ejecutar
```bash
streamlit run app.py
```
Se abre solo en tu navegador (http://localhost:8501).

---

## 🧭 Flujo de uso
1. **Buscar** → escribe tu tema, filtra por año/autor/citas, y marca ✅ los artículos útiles.
2. **Redactar** → elige la sección (Introducción, Marco teórico, etc.) y genera el borrador con citas.
3. **Exportar** → descarga tu `.docx` con las secciones y la bibliografía APA.

---

## 🗂️ Estructura
```
ThesisAI/
├─ app.py                  # interfaz (Streamlit)
├─ requirements.txt
├─ .env.example
└─ thesisai/
   ├─ config.py            # carga de claves (.env)
   ├─ providers/           # IAs gratuitas + enrutador (Gemini/Groq/Ollama)
   ├─ search/              # buscador (OpenAlex + Crossref)
   ├─ writing/             # redactor asistido con citas
   ├─ citations/           # referencias APA 7
   └─ export/              # exportar a Word (.docx)
```

## 🔜 Próximas fases
- Subir tus propios PDFs y que el bot los lea (RAG).
- Más formatos de cita (IEEE, Vancouver).
- Verificación de fidelidad de citas y control de similitud.
- Editor con control de versiones.

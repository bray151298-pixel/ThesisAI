# 🚀 Publicar ThesisAI en internet (gratis, privada con contraseña)

Guía para subir la app a **Streamlit Community Cloud**. URL final: `https://TUNOMBRE.streamlit.app`

> Tus claves de IA **no** se suben con el código. Van aparte, en los "Secrets" de Streamlit.

---

## Paso 1 — Crear cuenta en GitHub (si no tienes)
1. Entra a https://github.com y regístrate (gratis).
2. Verifica tu correo.

## Paso 2 — Subir el código a GitHub
Tienes dos formas:

### Opción A — Con GitHub Desktop (más fácil, sin comandos)
1. Descarga **GitHub Desktop**: https://desktop.github.com
2. Inicia sesión con tu cuenta de GitHub.
3. **File → Add local repository →** elige la carpeta `D:\ThesisAI`.
4. Te ofrecerá crear el repositorio: acepta.
5. Pon un nombre (ej. `thesisai`) y marca **Private** (privado).
6. Clic en **Publish repository**.

### Opción B — Con comandos (si tienes Git)
```bash
cd /d D:\ThesisAI
git init
git add .
git commit -m "ThesisAI - version inicial"
```
Luego crea un repo **privado** en GitHub llamado `thesisai` y sigue las instrucciones que te da GitHub para "push".

> ✅ Gracias al `.gitignore`, tu archivo `.env` con las claves **NO se sube**. Verifícalo: en GitHub no debe aparecer `.env` (sí puede aparecer `.env.example`, que está vacío).

## Paso 3 — Desplegar en Streamlit Cloud
1. Entra a https://share.streamlit.io e inicia sesión **con tu GitHub**.
2. Clic en **Create app → Deploy a public app from GitHub** (aunque el repo sea privado, funciona).
3. Selecciona:
   - **Repository:** `tu-usuario/thesisai`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Clic en **Advanced settings → Secrets** y pega tus claves (formato de `.streamlit/secrets.toml.example`):
   ```toml
   GEMINI_API_KEY = "tu_clave_gemini"
   GEMINI_MODEL = "gemini-flash-latest"
   GROQ_API_KEY = "tu_clave_groq"
   CORE_API_KEY = "tu_clave_core"
   APP_PASSWORD = "una_contrasena_secreta"
   CONTACT_EMAIL = "1007720181@unajma.edu.pe"
   ```
5. Clic en **Deploy**. Espera 1-2 minutos.

## Paso 4 — Listo ✅
- Tu app queda en `https://TUNOMBRE.streamlit.app`
- Al entrar pedirá la **contraseña** (`APP_PASSWORD`). Solo tú la sabes.

---

## Actualizar la app después
Cada vez que cambies el código y hagas **push** a GitHub (o "Commit + Push" en GitHub Desktop), Streamlit Cloud **actualiza la app sola**.

## Cambiar el nombre del subdominio
En Streamlit Cloud: **App → Settings → General → App URL**.

## ¿Dominio propio (ej. thesisai.com)?
Streamlit Cloud gratis no permite dominio propio. Si algún día lo quieres, hay que comprar un dominio (~$1-12/año) y usar otro hosting (Render). Para uso personal, el `.streamlit.app` gratis es suficiente.

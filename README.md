# MentorTI Nexus

MentorTI Nexus es un asistente inteligente de capacitación para el área de TI que combina un backend FastAPI con un frontend React/Vite y un agente RAG (Retrieval-Augmented Generation). El proyecto ofrece respuestas técnicas a preguntas sobre redes, VPN, procedimientos, documentación interna y más.

# Sistema Funcionando
![image alt] (https://github.com/RemixGG06/AluraChallengeRag/blob/e357b388abbfeb9359f4747aa89a191db627e955/Sistema%20Funcionando.jpeg)

## Arquitectura de la solución

- `backend/`
  - `backend/api/`: API REST construida con FastAPI.
  - `backend/llm/`: Lógica del agente conversacional basada en LangChain y un modelo compatible con Groq.
  - `backend/rag/`: Vector store FAISS para búsquedas semánticas de documentos internos y herramientas de fallback web.
  - `backend/config/`: Configuración centralizada y carga de variables de entorno.
  - `backend/common/cache.py`: Caché en memoria con TTL para evitar llamadas repetidas al LLM (se invalida automáticamente al subir documentos).
- `frontend/`
  - Aplicación web React con Vite que consume la API de chat y ofrece vistas para chat, administración y acerca de.
- `data/`
  - Almacena el índice FAISS (`data/faiss_index`) y documentos de ejemplo (`data/raw/`).

## Tecnologías y herramientas utilizadas

- Backend:
  - Python
  - FastAPI
  - Uvicorn
  - LangChain 1.x
  - FAISS
  - HuggingFace Inference API
  - DDGS (DuckDuckGo) para fallback web
  - python-dotenv
  - Caché en memoria con TTL (respuestas repetidas no llaman al LLM)
- Frontend:
  - React
  - Vite
  - React Router DOM
  - i18next (internacionalización)
  - React Markdown
- Pruebas:
  - Pytest
  - Vitest
- Otros:
  - GitHub para control de versiones
  - `.env.example` para configuración local segura

## Instrucciones para ejecutar el proyecto

### 1. Clonar el repositorio

```powershell
git clone https://github.com/tu-usuario/nombre-del-repo.git
cd nombre-del-repo
```

### 2. Configurar el entorno backend

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Luego edita `.env` y agrega al menos:

```env
OPENROUTER_API_KEY=tu_api_key_aqui
HUGGINGFACE_API_KEY=tu_api_key_aqui
```

Opcionalmente puedes configurar el caché de respuestas del chat:

```env
CACHE_TTL_SECONDS=600       # Tiempo de vida de cada respuesta en caché (default: 600)
CACHE_MAXSIZE=500           # Máximo de entradas en caché (default: 500)
```

### 3. Iniciar el backend

```powershell
uvicorn backend.api.main:app --reload --port 8000
```

### 4. Iniciar el frontend

```powershell
cd frontend
npm install
npm run dev
```

### 5. Acceder a la aplicación

Abre tu navegador en:

- Frontend: `http://localhost:5173`
- API de desarrollo: `http://localhost:8000`

## Ejemplos de preguntas que el agente puede responder

- ¿Cómo configuro una VPN para acceso remoto en la red de la empresa?
- ¿Dónde encuentro el procedimiento de backups diarios?
- ¿Qué documentos internos existen sobre seguridad de contraseñas?
- ¿Cuál es el paso a paso para recuperar una contraseña de administrador?
- ¿Qué hacer si el servidor no responde en la red local?

## Ejemplos de respuestas generadas por el agente

- Respuesta de conocimiento interno:
  - "Según el manual interno de VPN, primero debes validar el certificado, luego configurar el cliente con la dirección del gateway y finalmente autenticarte con usuario y contraseña.
  - Manual citado: `manual_vpn_red.md`."

- Respuesta de fallback web:
  - "No encontré un documento interno con la respuesta completa, pero según fuentes confiables en internet, debes revisar la configuración DNS del adaptador de red y confirmar que el servidor esté accesible desde la subred local."

- Respuesta sobre documentos disponibles:
  - "Estos son los documentos indexados en la base de conocimiento interna:
    - `manual_vpn_red.md` (Redes, 12 fragmentos)
    - `contactos_soporte.csv` (Soporte, 5 fragmentos)
    - `procedimiento_backups.html` (Operaciones, 8 fragmentos)"

## Despliegue

### Backend (Render)

Revisa `render.yaml` para la configuración de servicio web:

- **BuildCommand**: `pip install -r requirements.txt && python -m backend.scripts.ingest_samples && cd frontend && npm ci && npm run build`
  - Ingesta los documentos de `data/samples/` en el índice FAISS durante el build.
- **Variables de entorno obligatorias** (definir en el dashboard de Render):
  - `OPENROUTER_API_KEY` — API key de Groq.
  - `HUGGINGFACE_API_KEY` — API key de HuggingFace (necesaria para los embeddings).
- **Modelos** (vía Groq):
  - Primario: `llama-3.3-70b-versatile`
  - Respaldo: `llama-3.1-8b-instant`

### Frontend (Vercel)

`frontend/vercel.json` reescribe las rutas `/api/*` hacia el backend en Render. Configura la variable `VITE_API_URL` solo si usas un dominio distinto (por defecto usa la rewrite de Vercel).

## Caché de respuestas

El endpoint `/api/chat` incorpora un caché en memoria (`backend/common/cache.py`):

- **Clave**: pregunta normalizada (minúsculas, sin espacios extra) + idioma.
- **TTL**: configurable vía `CACHE_TTL_SECONDS` (default: 600 segundos / 10 min).
- **Máximo de entradas**: configurable vía `CACHE_MAXSIZE` (default: 500).
- **Invalidación**: al subir documentos nuevos mediante `/api/admin/upload` se vacía la caché automáticamente.
- Si la misma pregunta (en el mismo idioma) se repite antes de que expire la caché, se devuelve la respuesta anterior sin llamar al LLM. Esto reduce el consumo de cuota en Groq free.

## Configuración de modelos

Los modelos se configuran vía variables de entorno:

| Variable | Default | Descripción |
|---|---|---|
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Modelo principal (Groq) |
| `FALLBACK_LLM_MODELS` | `llama-3.1-8b-instant` | Modelos de respaldo (separados por coma) |
| `LLM_TEMPERATURE` | `0.2` | Temperatura del modelo |
| `OPENROUTER_BASE_URL` | `https://api.groq.com/openai/v1` | Endpoint compatible OpenAI |

## Notas adicionales

- Nunca subas archivos con credenciales reales al repositorio.
- Usa `.env.example` como plantilla para crear tu `.env` local.
- El agente está diseñado para priorizar primero la base de conocimiento interna y solo recurrir a la web si la información interna no es suficiente.
- En el plan free de Render los archivos subidos vía `/api/admin/upload` se pierden al redeployar (no hay disco persistente). El índice construido durante el build es la fuente inicial; para persistir subidas se necesita un plan de pago con Persistent Disk.

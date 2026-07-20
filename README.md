# MentorTI Nexus

MentorTI Nexus es un asistente inteligente de capacitación para el área de TI que combina un backend FastAPI con un frontend React/Vite y un agente RAG (Retrieval-Augmented Generation). El proyecto ofrece respuestas técnicas a preguntas sobre redes, VPN, procedimientos, documentación interna y más.

## Arquitectura de la solución

- `backend/`
  - `backend/api/`: API REST construida con FastAPI.
  - `backend/llm/`: Lógica del agente conversacional basada en LangChain y un modelo compatible con OpenRouter.
  - `backend/rag/`: Vector store FAISS para búsquedas semánticas de documentos internos y herramientas de fallback web.
  - `backend/config/`: Configuración centralizada y carga de variables de entorno.
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
  - DuckDuckGo Search para fallback web
  - python-dotenv
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
  - “Según el manual interno de VPN, primero debes validar el certificado, luego configurar el cliente con la dirección del gateway y finalmente autenticarte con usuario y contraseña.
  - Manual citado: `manual_vpn_red.md`.”

- Respuesta de fallback web:
  - “No encontré un documento interno con la respuesta completa, pero según fuentes confiables en internet, debes revisar la configuración DNS del adaptador de red y confirmar que el servidor esté accesible desde la subred local.”

- Respuesta sobre documentos disponibles:
  - “Estos son los documentos indexados en la base de conocimiento interna:
    - `manual_vpn_red.md` (Redes, 12 fragmentos)
    - `contactos_soporte.csv` (Soporte, 5 fragmentos)
    - `procedimiento_backups.html` (Operaciones, 8 fragmentos)”

## Notas adicionales

- Nunca subas archivos con credenciales reales al repositorio.
- Usa `.env.example` como plantilla para crear tu `.env` local.
- El agente está diseñado para priorizar primero la base de conocimiento interna y solo recurrir a la web si la información interna no es suficiente.

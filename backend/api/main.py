"""MentorTI Nexus — Punto de entrada de la API (FastAPI).

Ejecutar:
    uvicorn backend.api.main:app --reload --port 8000
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.routes.about import router as about_router
from backend.api.routes.admin import router as admin_router
from backend.api.routes.chat import router as chat_router
from backend.config.settings import settings, BASE_DIR

app = FastAPI(
    title="MentorTI Nexus API",
    description="Backend API para el sistema de capacitación Agentic RAG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(about_router, prefix="/api/about", tags=["about"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "MentorTI Nexus"}


# --- Servir frontend estático en producción ---
frontend_dist = BASE_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(frontend_dist / "assets")),
        name="assets",
    )

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        file = frontend_dist / path
        if file.is_file():
            return FileResponse(str(file))
        index = frontend_dist / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return {"error": "Frontend no encontrado"}

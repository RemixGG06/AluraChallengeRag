"""Tests de integración de la API FastAPI (TestClient, sin red real).

Cubre los endpoints que consume el frontend React:
- GET  /api/health
- GET  /api/about
- GET  /api/admin/inventory
- POST /api/admin/upload
- POST /api/chat

El agente/LLM se sustituye por un doble para no hacer llamadas de red.
"""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)


class TestHealth:
    def test_health_ok(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "MentorTI" in body["service"]


class TestAbout:
    def test_about_estructura(self):
        response = client.get("/api/about")
        assert response.status_code == 200
        body = response.json()

        assert body["app_name"]
        assert body["purpose"]
        # Modelos y retrieval
        assert "llm" in body["models"]
        assert "embeddings" in body["models"]
        assert body["retrieval"]["k"] > 0
        assert 0.0 <= body["retrieval"]["threshold"] <= 1.0
        # Catálogos
        assert "operaciones" in body["departments"]
        assert ".pdf" in body["formats"]
        assert set(body["languages"]) == {"es", "pt"}
        # Rutas de datos
        assert "faiss_index" in body["datastore"]["faiss_index_path"]


class TestInventory:
    def test_inventory_sin_indice_devuelve_vacio(self, monkeypatch):
        monkeypatch.setattr(
            "backend.api.routes.admin.list_indexed_sources", lambda: []
        )
        response = client.get("/api/admin/inventory")
        assert response.status_code == 200
        body = response.json()
        assert body["items"] == []
        assert body["total_documents"] == 0
        assert body["total_chunks"] == 0
        assert body["total_departments"] == 0

    def test_inventory_con_documentos(self, monkeypatch):
        monkeypatch.setattr(
            "backend.api.routes.admin.list_indexed_sources",
            lambda: [
                {"source": "manual_red.md", "department": "operaciones", "chunks": 4},
                {"source": "normativa_rh.pdf", "department": "rh", "chunks": 6},
            ],
        )
        response = client.get("/api/admin/inventory")
        assert response.status_code == 200
        body = response.json()
        assert body["total_documents"] == 2
        assert body["total_chunks"] == 10
        assert body["total_departments"] == 2
        assert body["items"][0]["source"] == "manual_red.md"


class TestUpload:
    def test_upload_archivo_valido(self, monkeypatch, tmp_path):
        monkeypatch.setattr("backend.api.routes.admin.settings",
                            type("S", (), {"raw_docs_path": tmp_path})())
        monkeypatch.setattr(
            "backend.api.routes.admin.ingest_file", lambda path, department: 3
        )

        files = {"files": ("manual.md", io.BytesIO(b"# Manual\ncontenido"), "text/markdown")}
        data = {"department": "operaciones"}
        response = client.post("/api/admin/upload", files=files, data=data)

        assert response.status_code == 200
        result = response.json()["results"][0]
        assert result["name"] == "manual.md"
        assert result["success"] is True
        assert result["chunks"] == 3

    def test_upload_extension_no_soportada(self, monkeypatch, tmp_path):
        monkeypatch.setattr("backend.api.routes.admin.settings",
                            type("S", (), {"raw_docs_path": tmp_path})())

        files = {"files": ("virus.exe", io.BytesIO(b"MZ"), "application/octet-stream")}
        response = client.post("/api/admin/upload", files=files)

        assert response.status_code == 200
        result = response.json()["results"][0]
        assert result["success"] is False
        assert "Formato no soportado" in result["error"]


class TestChat:
    def test_chat_respuesta_ok(self, monkeypatch):
        def _fake_ask(question, chat_history=None):
            return {
                "answer": "Respuesta del mentor.",
                "source_type": "internal",
                "sources": [{"source": "manual_red.md", "department": "operaciones", "score": 0.9}],
                "model": "modelo-test",
            }

        # La ruta importa ask dentro de la función, así que parchear el
        # símbolo en el módulo de origen es suficiente.
        monkeypatch.setattr("backend.llm.agent.ask", _fake_ask)

        response = client.post(
            "/api/chat",
            json={
                "question": "¿cuál es la contraseña del wifi?",
                "history": [],
                "lang": "es",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["answer"] == "Respuesta del mentor."
        assert body["source_type"] == "internal"
        assert body["model"] == "modelo-test"
        assert body["sources"][0]["source"] == "manual_red.md"

    def test_chat_valida_idioma(self):
        response = client.post(
            "/api/chat",
            json={"question": "hola", "history": [], "lang": "fr"},
        )
        assert response.status_code == 422  # validación Pydantic

    def test_chat_rechaza_pregunta_vacia(self):
        response = client.post(
            "/api/chat",
            json={"question": "", "history": [], "lang": "es"},
        )
        assert response.status_code == 422

"""Configuración centralizada de MentorTI Nexus.

Todas las variables se cargan desde el entorno (archivo .env en desarrollo
local, variables de entorno del sistema en producción/OCI).

Regla de seguridad: NUNCA hardcodear secretos en este archivo.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Raíz del proyecto (carpeta que contiene al paquete backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    """Configuración inmutable de la aplicación."""

    # --- LLM: OpenRouter (endpoint compatible con OpenAI) ---
    openrouter_api_key: str = field(
        default_factory=lambda: os.getenv("OPENROUTER_API_KEY", "")
    )
    openrouter_base_url: str = field(
        default_factory=lambda: os.getenv(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
    )
    llm_model: str = field(
        default_factory=lambda: os.getenv(
            "LLM_MODEL", "google/gemma-4-26b-a4b-it:free"
        )
    )
    llm_temperature: float = field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.2"))
    )
    # Modelos de respaldo ante rate limits 429 de los :free (se prueban en orden)
    llm_fallback_models: list[str] = field(
        default_factory=lambda: [
            m.strip()
            for m in os.getenv(
                "FALLBACK_LLM_MODELS",
                "nvidia/nemotron-3-nano-30b-a3b:free,tencent/hy3:free",
            ).split(",")
            if m.strip()
        ]
    )

    # --- Embeddings remotos vía HuggingFace Inference API ---
    huggingface_api_key: str = field(
        default_factory=lambda: os.getenv("HUGGINGFACE_API_KEY", "")
    )
    embedding_model: str = field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        )
    )

    # --- Rutas de datos ---
    faiss_index_path: Path = field(
        default_factory=lambda: BASE_DIR
        / os.getenv("FAISS_INDEX_PATH", "data/faiss_index")
    )
    raw_docs_path: Path = field(
        default_factory=lambda: BASE_DIR / os.getenv("RAW_DOCS_PATH", "data/raw")
    )

    # --- Chunking ---
    chunk_size: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_SIZE", "1000"))
    )
    chunk_overlap: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "200"))
    )

    # --- Retrieval (umbral para decidir fallback web) ---
    # Calibrado en Fase 5 con documentos reales es/pt (KB-09): consultas
    # cubiertas puntúan 0.25-0.74; off-topic puntúa ~0.00. Umbral 0.25.
    retriever_k: int = field(
        default_factory=lambda: int(os.getenv("RETRIEVER_K", "4"))
    )
    score_threshold: float = field(
        default_factory=lambda: float(os.getenv("SCORE_THRESHOLD", "0.25"))
    )

    # --- Aplicación ---
    app_name: str = field(
        default_factory=lambda: os.getenv("APP_NAME", "MentorTI Nexus")
    )
    app_default_lang: str = field(
        default_factory=lambda: os.getenv("APP_DEFAULT_LANG", "es")
    )

    # --- CORS (producción) ---
    cors_origins: list[str] = field(
        default_factory=lambda: [
            o.strip()
            for o in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://localhost:3000",
            ).split(",")
            if o.strip()
        ]
    )

    def validate(self) -> list[str]:
        """Retorna lista de errores de configuración (vacía si todo está ok)."""
        errors: list[str] = []
        if not self.openrouter_api_key:
            errors.append(
                "OPENROUTER_API_KEY no está definida. "
                "Copia .env.example a .env y completa tu API key."
            )
        return errors


# Instancia global de solo lectura para importar en el resto del proyecto
settings = Settings()

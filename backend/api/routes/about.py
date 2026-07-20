"""Ruta /api/about — información técnica del sistema."""

from __future__ import annotations

from fastapi import APIRouter

from backend.config.i18n import DEPARTMENTS, SUPPORTED_LANGS
from backend.config.settings import settings
from backend.rag.loaders.document_loader import SUPPORTED_EXTENSIONS

router = APIRouter()


@router.get("")
def get_about_info():
    return {
        "app_name": settings.app_name,
        "purpose": (
            "Sistema de capacitación y autoaprendizaje basado en IA (Agentic "
            "RAG) que acelera el onboarding de practicantes de TI respondiendo "
            "dudas técnicas con los manuales internos y, si no bastan, con "
            "búsqueda web en fuentes confiables."
        ),
        "models": {
            "llm": settings.llm_model,
            "fallbacks": settings.llm_fallback_models,
            "temperature": settings.llm_temperature,
            "embeddings": settings.embedding_model,
            "provider": "HuggingFace Inference API",
        },
        "retrieval": {
            "k": settings.retriever_k,
            "threshold": settings.score_threshold,
        },
        "departments": list(DEPARTMENTS),
        "formats": sorted(SUPPORTED_EXTENSIONS),
        "languages": list(SUPPORTED_LANGS),
        "datastore": {
            "faiss_index_path": str(settings.faiss_index_path),
            "raw_docs_path": str(settings.raw_docs_path),
        },
    }

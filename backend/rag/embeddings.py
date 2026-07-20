"""Embeddings multilingües remotos vía HuggingFace Inference API.

Modelo: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
Corre en servidores de HuggingFace, no requiere GPU local ni torch.

Requiere HUGGINGFACE_API_KEY en .env (gratis en huggingface.co/settings/tokens).
Sin API key funciona con rate limits reducidos (no recomendado para producción).
"""

from __future__ import annotations

from functools import lru_cache
from math import sqrt

from huggingface_hub import InferenceClient
from langchain_core.embeddings import Embeddings

from backend.config.settings import settings


def _l2_normalize(vector: list[float]) -> list[float]:
    """Normaliza un vector a norma L2 = 1."""
    norm = sqrt(sum(x * x for x in vector))
    return [x / norm for x in vector] if norm > 0 else vector


class RemoteMultilingualEmbeddings(Embeddings):
    """Embeddings vía HuggingFace Inference API, interfaz Embeddings de LangChain.

    Los vectores se normalizan (norma L2 = 1) para que la similitud coseno
    sea equivalente al producto punto, manteniendo umbrales estables entre 0 y 1.
    """

    def __init__(self, model_name: str | None = None, api_key: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self._client = InferenceClient(
            model=self.model_name,
            token=api_key or settings.huggingface_api_key or None,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self._client.feature_extraction(texts)
        return [_l2_normalize(vec) for vec in response]

    def embed_query(self, text: str) -> list[float]:
        response = self._client.feature_extraction(text)
        return _l2_normalize(response[0] if response and isinstance(response[0], list) else response)


@lru_cache(maxsize=1)
def get_embeddings() -> RemoteMultilingualEmbeddings:
    """Singleton: una sola instancia del cliente de embeddings."""
    return RemoteMultilingualEmbeddings()

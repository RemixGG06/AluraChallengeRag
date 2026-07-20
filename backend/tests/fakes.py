"""Utilidades compartidas para tests (embeddings falsos deterministas)."""

import hashlib
import math

from langchain_core.embeddings import Embeddings


class FakeEmbeddings(Embeddings):
    """Embeddings deterministas: mismo texto -> mismo vector normalizado.

    Permiten testear FAISS sin descargar el modelo real (offline, rápido).
    """

    def __init__(self, size: int = 16):
        self.size = size

    def _vector(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = [(digest[i % len(digest)] / 255.0) - 0.5 for i in range(self.size)]
        norm = math.sqrt(sum(v * v for v in values)) or 1.0
        return [v / norm for v in values]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)

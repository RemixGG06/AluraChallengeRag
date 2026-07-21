"""Tests de embeddings remotos con mocks que imitan la API real de HuggingFace.

El objetivo es reproducir el comportamiento de `feature_extraction` sin llamar
a la red: devuelve arrays numpy de numpy, lo que en producción causaba el error
"The truth value of an array with more than one element is ambiguous".
"""

from __future__ import annotations

import numpy as np

from backend.rag.embeddings import RemoteMultilingualEmbeddings


class _FakeInferenceClient:
    """Mock de huggingface_hub.InferenceClient para feature_extraction."""

    def __init__(self, *, query_shape, docs_shape):
        self._query_shape = query_shape
        self._docs_shape = docs_shape

    def feature_extraction(self, texts):
        if isinstance(texts, str):
            return np.ones(self._query_shape, dtype=np.float32)
        return np.ones(self._docs_shape, dtype=np.float32)


class TestRemoteMultilingualEmbeddings:
    def test_embed_query_con_array_2d_no_lanza_error(self):
        """Caso real: feature_extraction(text) -> shape (1, dim)."""
        emb = RemoteMultilingualEmbeddings.__new__(RemoteMultilingualEmbeddings)
        emb._client = _FakeInferenceClient(query_shape=(1, 384), docs_shape=(2, 384))

        result = emb.embed_query("hola")

        assert len(result) == 384
        assert all(isinstance(x, (float, np.floating)) for x in result)
        # Normalizado L2
        assert np.isclose(np.linalg.norm(result), 1.0)

    def test_embed_query_con_array_1d_no_lanza_error(self):
        """Caso defensivo: feature_extraction(text) -> shape (dim,)."""
        emb = RemoteMultilingualEmbeddings.__new__(RemoteMultilingualEmbeddings)
        emb._client = _FakeInferenceClient(query_shape=(384,), docs_shape=(2, 384))

        result = emb.embed_query("hola")

        assert len(result) == 384
        assert np.isclose(np.linalg.norm(result), 1.0)

    def test_embed_documents_itera_filas_del_array(self):
        """Caso real: feature_extraction(list) -> shape (n, dim)."""
        emb = RemoteMultilingualEmbeddings.__new__(RemoteMultilingualEmbeddings)
        emb._client = _FakeInferenceClient(query_shape=(1, 384), docs_shape=(3, 384))

        result = emb.embed_documents(["a", "b", "c"])

        assert len(result) == 3
        for vec in result:
            assert len(vec) == 384
            assert np.isclose(np.linalg.norm(vec), 1.0)

    def test_embed_query_con_lista_de_listas(self):
        """Caso hipotético: la API devuelve lista plana en lugar de array."""
        emb = RemoteMultilingualEmbeddings.__new__(RemoteMultilingualEmbeddings)

        class _FakeClientList:
            def feature_extraction(self, texts):
                if isinstance(texts, str):
                    return [1.0] * 384
                return [[1.0] * 384, [2.0] * 384]

        emb._client = _FakeClientList()
        result = emb.embed_query("hola")

        assert len(result) == 384
        assert np.isclose(np.linalg.norm(result), 1.0)

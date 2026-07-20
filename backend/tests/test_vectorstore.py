"""Tests del vector store FAISS (con embeddings falsos deterministas).

No se descarga el modelo real: se usa un embedding determinista basado en hash
para que los tests sean rápidos y offline. El smoke test con el modelo real se
ejecuta aparte (Fase 5).
"""

import hashlib
import math

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from backend.rag.vectorstore import (
    add_documents,
    create_vectorstore,
    has_relevant_results,
    ingest_file,
    list_indexed_sources,
    load_vectorstore,
    save_vectorstore,
    search_with_scores,
)


class FakeEmbeddings(Embeddings):
    """Embeddings deterministas: mismo texto -> mismo vector normalizado."""

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


@pytest.fixture()
def embeddings():
    return FakeEmbeddings()


@pytest.fixture()
def sample_docs():
    return [
        Document(
            page_content="La contraseña del WiFi de invitados se rota cada lunes.",
            metadata={"source": "manual_red.md", "department": "operaciones"},
        ),
        Document(
            page_content="Las vacaciones se solicitan en el portal de RH.",
            metadata={"source": "normativa_rh.pdf", "department": "rh"},
        ),
    ]


class TestCreateSaveLoad:
    def test_roundtrip_persistencia(self, tmp_path, embeddings, sample_docs):
        vs = create_vectorstore(sample_docs, embeddings=embeddings)
        save_vectorstore(vs, path=tmp_path)
        assert (tmp_path / "index.faiss").exists()

        loaded = load_vectorstore(path=tmp_path, embeddings=embeddings)
        assert loaded is not None

        # Los embeddings falsos no tienen semántica: se valida el roundtrip
        # con una consulta exacta al contenido de un documento indexado.
        query = "Las vacaciones se solicitan en el portal de RH."
        results = search_with_scores(loaded, query, k=1)
        assert len(results) == 1
        doc, score = results[0]
        assert doc.page_content == query
        assert score >= 0.99

    def test_load_sin_indice_retorna_none(self, tmp_path, embeddings):
        assert load_vectorstore(path=tmp_path, embeddings=embeddings) is None

    def test_create_sin_documentos_falla(self, embeddings):
        with pytest.raises(ValueError):
            create_vectorstore([], embeddings=embeddings)

    def test_busqueda_exacta_score_alto(self, embeddings, sample_docs):
        vs = create_vectorstore(sample_docs, embeddings=embeddings)
        query = "La contraseña del WiFi de invitados se rota cada lunes."
        results = search_with_scores(vs, query, k=2)
        best_doc, best_score = results[0]
        assert best_doc.page_content == query
        assert best_score >= 0.99


class TestAddDocuments:
    def test_agregar_a_indice_existente(self, embeddings, sample_docs):
        vs = create_vectorstore(sample_docs[:1], embeddings=embeddings)
        ids = add_documents(vs, sample_docs[1:])
        assert len(ids) == 1

        results = search_with_scores(vs, "vacaciones", k=2)
        assert len(results) == 2

    def test_agregar_lista_vacia(self, embeddings, sample_docs):
        vs = create_vectorstore(sample_docs, embeddings=embeddings)
        assert add_documents(vs, []) == []


class TestThreshold:
    def test_resultado_relevante_supera_umbral(self, embeddings, sample_docs):
        vs = create_vectorstore(sample_docs, embeddings=embeddings)
        query = "Las vacaciones se solicitan en el portal de RH."
        results = search_with_scores(vs, query, k=2)
        assert has_relevant_results(results, threshold=0.5)

    def test_lista_vacia_no_es_relevante(self):
        assert not has_relevant_results([], threshold=0.5)


class TestIngestFile:
    def test_ingesta_crea_indice_y_luego_agrega(self, tmp_path, embeddings):
        index_path = tmp_path / "index"
        doc1 = tmp_path / "manual.md"
        doc1.write_text("# Red\n\nLa VLAN de voz es la 40.", encoding="utf-8")
        doc2 = tmp_path / "inventario.csv"
        doc2.write_text("equipo,ip\nswitch-01,10.0.0.2\n", encoding="utf-8")

        chunks1 = ingest_file(
            doc1, department="operaciones", path=index_path, embeddings=embeddings
        )
        assert chunks1 >= 1
        assert (index_path / "index.faiss").exists()

        chunks2 = ingest_file(
            doc2, department="sistemas", path=index_path, embeddings=embeddings
        )
        assert chunks2 >= 1

        inventory = list_indexed_sources(path=index_path, embeddings=embeddings)
        sources = {item["source"] for item in inventory}
        assert sources == {"manual.md", "inventario.csv"}
        assert all(item["chunks"] >= 1 for item in inventory)

    def test_archivo_sin_texto_falla(self, tmp_path, embeddings):
        empty = tmp_path / "vacio.md"
        empty.write_text("", encoding="utf-8")
        with pytest.raises(ValueError, match="texto extraíble"):
            ingest_file(empty, path=tmp_path / "index", embeddings=embeddings)


class TestInventory:
    def test_inventario_vacio_sin_indice(self, tmp_path, embeddings):
        assert list_indexed_sources(path=tmp_path, embeddings=embeddings) == []

"""Vector store FAISS: creación, persistencia, búsqueda e ingesta.

El índice se persiste en disco (settings.faiss_index_path) para sobrevivir
reinicios de la aplicación.
"""

from __future__ import annotations

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from backend.config.settings import settings
from backend.rag.embeddings import get_embeddings
from backend.rag.loaders.document_loader import load_document, split_documents


def create_vectorstore(
    documents: list[Document], embeddings: Embeddings | None = None
) -> FAISS:
    """Crea un índice FAISS nuevo a partir de documentos.

    Se usa distancia COSENO porque los embeddings se normalizan (norma L2=1):
    la relevancia resultante equivale a la similitud coseno, adecuada para el
    umbral de decisión del fallback web.
    """
    if not documents:
        raise ValueError("No se puede crear el índice sin documentos.")
    return FAISS.from_documents(
        documents,
        embeddings or get_embeddings(),
        distance_strategy=DistanceStrategy.COSINE,
    )


def save_vectorstore(vectorstore: FAISS, path: str | Path | None = None) -> Path:
    """Persiste el índice en disco. Retorna la ruta usada."""
    path = Path(path or settings.faiss_index_path)
    path.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(path))
    return path


def load_vectorstore(
    path: str | Path | None = None, embeddings: Embeddings | None = None
) -> FAISS | None:
    """Carga el índice desde disco. Retorna None si aún no existe."""
    path = Path(path or settings.faiss_index_path)
    if not (path / "index.faiss").exists():
        return None
    return FAISS.load_local(
        str(path),
        embeddings or get_embeddings(),
        # El índice es generado por la propia aplicación (origen confiable)
        allow_dangerous_deserialization=True,
    )


def add_documents(vectorstore: FAISS, documents: list[Document]) -> list[str]:
    """Agrega documentos a un índice existente. Retorna los IDs asignados."""
    if not documents:
        return []
    return vectorstore.add_documents(documents)


def search_with_scores(
    vectorstore: FAISS, query: str, k: int | None = None
) -> list[tuple[Document, float]]:
    """Búsqueda semántica. Retorna lista de (documento, relevancia 0-1).

    Relevancia más alta = más relacionado con la consulta. Los scores se
    recortan al rango [0, 1] para mantener estable la lógica del umbral.
    """
    results = vectorstore.similarity_search_with_relevance_scores(
        query, k=k or settings.retriever_k
    )
    return [(doc, max(0.0, min(1.0, float(score)))) for doc, score in results]


def has_relevant_results(
    results: list[tuple[Document, float]], threshold: float | None = None
) -> bool:
    """True si al menos un resultado supera el umbral de relevancia.

    Es el criterio que usa el agente para decidir el fallback web.
    """
    threshold = settings.score_threshold if threshold is None else threshold
    return any(score >= threshold for _, score in results)


def ingest_file(
    file_path: str | Path,
    department: str = "general",
    path: str | Path | None = None,
    embeddings: Embeddings | None = None,
) -> int:
    """Pipeline completo: cargar → chunkear → indexar → persistir.

    Si el índice no existe lo crea; si existe, agrega los nuevos chunks.
    Retorna el número de chunks indexados.
    """
    documents = load_document(file_path, department=department)
    if not documents:
        raise ValueError(f"El archivo no contiene texto extraíble: {file_path}")
    chunks = split_documents(documents)

    vectorstore = load_vectorstore(path=path, embeddings=embeddings)
    if vectorstore is None:
        vectorstore = create_vectorstore(chunks, embeddings=embeddings)
    else:
        add_documents(vectorstore, chunks)
    save_vectorstore(vectorstore, path=path)
    return len(chunks)


def list_indexed_sources(
    path: str | Path | None = None, embeddings: Embeddings | None = None
) -> list[dict]:
    """Inventario de documentos indexados (para la vista admin).

    Retorna lista de dicts: {source, department, chunks}.
    """
    vectorstore = load_vectorstore(path=path, embeddings=embeddings)
    if vectorstore is None:
        return []
    # Nota: docstore._dict es API interna de InMemoryDocstore; es la vía
    # disponible en langchain-community para inspeccionar el inventario.
    inventory: dict[str, dict] = {}
    for doc in vectorstore.docstore._dict.values():
        source = doc.metadata.get("source", "desconocido")
        if source not in inventory:
            inventory[source] = {
                "source": source,
                "department": doc.metadata.get("department", "general"),
                "chunks": 0,
            }
        inventory[source]["chunks"] += 1
    return sorted(inventory.values(), key=lambda item: item["source"])

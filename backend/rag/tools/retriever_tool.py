"""Tool de búsqueda en la base de conocimiento interna (FAISS).

Es la PRIMERA herramienta que el agente debe usar. Su salida incluye un
marcador de relevancia explícito para que el LLM decida si responde con los
documentos internos o si debe activar el fallback web.
"""

from __future__ import annotations

from langchain_core.tools import tool

from backend.config.settings import settings
from backend.rag.vectorstore import (
    has_relevant_results,
    load_vectorstore,
    search_with_scores,
)

# Marcadores que el system prompt del agente interpreta
MARK_SUFFICIENT = "[FUENTE INTERNA - RELEVANCIA SUFICIENTE]"
MARK_INSUFFICIENT = "[FUENTE INTERNA - RELEVANCIA INSUFICIENTE]"
MARK_EMPTY = "[FUENTE INTERNA - SIN DOCUMENTOS]"


def search_knowledge_base(
    query: str,
    vectorstore=None,
    k: int | None = None,
    threshold: float | None = None,
) -> tuple[str, list[dict]]:
    """Busca en la base interna. Retorna (texto_para_el_llm, fuentes).

    `fuentes` es una lista de dicts con metadata de los fragmentos usados,
    pensada para mostrar en la UI (indicador de fuente).
    """
    if vectorstore is None:
        vectorstore = load_vectorstore()
    if vectorstore is None:
        return (
            f"{MARK_EMPTY} La base de conocimiento está vacía. "
            "ACCIÓN: usa la herramienta buscar_en_web.",
            [],
        )

    results = search_with_scores(vectorstore, query, k=k)
    threshold = settings.score_threshold if threshold is None else threshold

    if not has_relevant_results(results, threshold):
        best = max((score for _, score in results), default=0.0)
        return (
            f"{MARK_INSUFFICIENT} (mejor relevancia: {best:.2f} < umbral "
            f"{threshold:.2f}). Los manuales internos no cubren esta duda. "
            "ACCIÓN: usa la herramienta buscar_en_web.",
            [],
        )

    lines = [f"{MARK_SUFFICIENT} Fragmentos de los manuales internos:"]
    sources = []
    for i, (doc, score) in enumerate(results, start=1):
        if score < threshold:
            continue
        lines.append(
            f"\n--- Fragmento {i} (manual: {doc.metadata.get('source')} | "
            f"departamento: {doc.metadata.get('department')} | "
            f"relevancia: {score:.2f}) ---\n{doc.page_content}"
        )
        sources.append(
            {
                "source": doc.metadata.get("source", "desconocido"),
                "department": doc.metadata.get("department", "general"),
                "score": round(score, 3),
            }
        )
    return "\n".join(lines), sources


def create_retriever_tool(vectorstore=None):
    """Fábrica del tool LangChain (permite inyectar un vectorstore en tests)."""

    @tool("buscar_base_conocimiento")
    def _tool(query: str) -> str:
        """Busca la respuesta en los manuales internos de la empresa (base
        vectorial FAISS). Úsala SIEMPRE primero, antes que cualquier otra
        herramienta. Devuelve fragmentos con su relevancia; si la relevancia
        es INSUFICIENTE, debes usar buscar_en_web."""
        text, _ = search_knowledge_base(query, vectorstore=vectorstore)
        return text

    return _tool

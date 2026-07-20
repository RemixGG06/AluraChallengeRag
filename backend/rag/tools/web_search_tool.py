"""Tool de fallback web con DuckDuckGo restringido a fuentes confiables.

Se activa SOLO cuando la base interna no cubre la duda (relevancia
insuficiente). Los resultados se priorizan por dominios técnicos confiables
(documentación oficial de vendors, comunidades reconocidas) para evitar
contenido no verificado.
"""

from __future__ import annotations

from urllib.parse import urlparse

from duckduckgo_search import DDGS
from langchain_core.tools import tool

# Dominios técnicos confiables (documentación oficial y comunidades validadas)
TRUSTED_DOMAINS = {
    # Vendors / documentación oficial
    "learn.microsoft.com", "support.microsoft.com", "docs.oracle.com",
    "cisco.com", "ubuntu.com", "access.redhat.com", "docs.aws.amazon.com",
    "cloud.google.com", "kubernetes.io", "docs.docker.com", "python.org",
    "git-scm.com", "developer.mozilla.org", "ibm.com",
    # Comunidades técnicas con revisión por pares
    "stackoverflow.com", "serverfault.com", "superuser.com",
    # Enciclopedias y documentación de referencia
    "wikipedia.org",
}

MARK_WEB = "[FUENTE EXTERNA - WEB]"


def _domain(url: str) -> str:
    """Extrae el dominio registrable simple de una URL."""
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def search_web(query: str, max_results: int = 5) -> tuple[str, list[dict]]:
    """Busca en la web priorizando fuentes confiables.

    Retorna (texto_para_el_llm, fuentes). Degrada elegantemente ante rate
    limits o falta de conectividad: informa al LLM en lugar de lanzar error.
    """
    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=max_results * 2))
    except Exception as exc:  # noqa: BLE001 - rate limit / sin conexión
        return (
            f"{MARK_WEB} La búsqueda web no está disponible en este momento "
            f"({type(exc).__name__}). Informa al usuario que lo intente de "
            "nuevo en unos minutos.",
            [],
        )

    if not raw:
        return (
            f"{MARK_WEB} No se encontraron resultados en internet para esta "
            "consulta.",
            [],
        )

    trusted = [r for r in raw if _domain(r.get("href", "")) in TRUSTED_DOMAINS]
    others = [r for r in raw if r not in trusted]
    ordered = (trusted + others)[:max_results]

    header = (
        f"{MARK_WEB} Resultados de internet (fuentes confiables "
        "priorizadas):"
    )
    lines = [header]
    sources = []
    for i, result in enumerate(ordered, start=1):
        url = result.get("href", "")
        is_trusted = result in trusted
        tag = "CONFIABLE" if is_trusted else "NO VERIFICADA"
        lines.append(
            f"\n--- Resultado {i} [{tag}] ---\n"
            f"Título: {result.get('title', '')}\n"
            f"URL: {url}\n"
            f"Resumen: {result.get('body', '')}"
        )
        sources.append(
            {
                "source": result.get("title", url),
                "url": url,
                "trusted": is_trusted,
            }
        )
    return "\n".join(lines), sources


def create_web_search_tool(max_results: int = 5):
    """Fábrica del tool LangChain."""

    @tool("buscar_en_web")
    def _tool(query: str) -> str:
        """Busca la solución en internet (DuckDuckGo) cuando los manuales
        internos NO cubren la duda. Prioriza documentación oficial y fuentes
        técnicas confiables. Úsala solo como fallback."""
        text, _ = search_web(query, max_results=max_results)
        return text

    return _tool

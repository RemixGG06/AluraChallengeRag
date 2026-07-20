"""Tests de las tools del agente (retriever interno + fallback web)."""

from langchain_core.documents import Document

from backend.rag.vectorstore import create_vectorstore
from backend.tests.fakes import FakeEmbeddings
from backend.rag.tools.retriever_tool import (
    MARK_EMPTY,
    MARK_INSUFFICIENT,
    MARK_SUFFICIENT,
    create_retriever_tool,
    search_knowledge_base,
)
from backend.rag.tools.web_search_tool import MARK_WEB, create_web_search_tool, search_web

QUERY_VPN = "La contraseña del WiFi de invitados se rota cada lunes."


def _vs_con_manual():
    docs = [
        Document(
            page_content=QUERY_VPN,
            metadata={"source": "manual_red.md", "department": "operaciones"},
        )
    ]
    return create_vectorstore(docs, embeddings=FakeEmbeddings())


class TestRetrieverTool:
    def test_sin_indice_pide_fallback(self, monkeypatch):
        monkeypatch.setattr("backend.rag.tools.retriever_tool.load_vectorstore", lambda: None)
        text, sources = search_knowledge_base("cualquier cosa")
        assert MARK_EMPTY in text
        assert sources == []

    def test_relevancia_suficiente_devuelve_fuentes(self):
        vs = _vs_con_manual()
        text, sources = search_knowledge_base(QUERY_VPN, vectorstore=vs)
        assert MARK_SUFFICIENT in text
        assert "manual_red.md" in text
        assert len(sources) == 1
        assert sources[0]["source"] == "manual_red.md"
        assert sources[0]["department"] == "operaciones"

    def test_relevancia_insuficiente_recomienda_web(self):
        vs = _vs_con_manual()
        # Umbral > 1 fuerza la insuficiencia de forma determinista
        text, sources = search_knowledge_base(
            QUERY_VPN, vectorstore=vs, threshold=1.5
        )
        assert MARK_INSUFFICIENT in text
        assert "buscar_en_web" in text
        assert sources == []

    def test_tool_langchain_invocable(self):
        vs = _vs_con_manual()
        tool = create_retriever_tool(vectorstore=vs)
        assert tool.name == "buscar_base_conocimiento"
        salida = tool.invoke(QUERY_VPN)
        assert isinstance(salida, str)
        assert MARK_SUFFICIENT in salida


class _FakeDDGS:
    """DuckDuckGo falso: 1 resultado confiable y 1 no verificado."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def text(self, query, max_results=10):
        return iter(
            [
                {
                    "title": "Blog random de Juan",
                    "href": "https://juanblogs.wordpress.com/post/123",
                    "body": "A mi me funcionó reiniciar el router.",
                },
                {
                    "title": "Microsoft Learn - VPN",
                    "href": "https://learn.microsoft.com/es-es/windows/vpn",
                    "body": "Documentación oficial de Microsoft sobre VPN.",
                },
            ]
        )


class TestWebSearchTool:
    def test_prioriza_fuentes_confiables(self, monkeypatch):
        monkeypatch.setattr("backend.rag.tools.web_search_tool.DDGS", _FakeDDGS)
        text, sources = search_web("error vpn windows")

        assert MARK_WEB in text
        # El resultado confiable debe ir primero pese a venir segundo de DDG
        assert sources[0]["trusted"] is True
        assert "learn.microsoft.com" in sources[0]["url"]
        assert sources[1]["trusted"] is False
        # La etiqueta CONFIABLE aparece antes que NO VERIFICADA en el texto
        assert text.index("CONFIABLE") < text.index("NO VERIFICADA")

    def test_degrada_elegantemente_si_falla(self, monkeypatch):
        class _DDGSQueFalla:
            def __enter__(self):
                raise RuntimeError("rate limit")

            def __exit__(self, *args):
                return False

        monkeypatch.setattr(
            "backend.rag.tools.web_search_tool.DDGS", _DDGSQueFalla
        )
        text, sources = search_web("lo que sea")
        assert MARK_WEB in text
        assert "no está disponible" in text
        assert sources == []

    def test_tool_langchain_invocable(self, monkeypatch):
        monkeypatch.setattr("backend.rag.tools.web_search_tool.DDGS", _FakeDDGS)
        tool = create_web_search_tool()
        assert tool.name == "buscar_en_web"
        assert MARK_WEB in tool.invoke("error vpn")

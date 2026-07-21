"""Tests del agente MentorTI Nexus (sin llamadas de red al LLM)."""

import dataclasses

from langchain_core.messages import AIMessage

from backend.config.settings import settings
from backend.llm.agent import SYSTEM_PROMPT, SourceCollector, ask, create_mentor_agent
from backend.rag.vectorstore import create_vectorstore
from langchain_core.documents import Document
from backend.tests.fakes import FakeEmbeddings


class TestSourceCollector:
    def test_sin_fuentes_es_none(self):
        assert SourceCollector().source_type == "none"

    def test_solo_internas_es_internal(self):
        collector = SourceCollector(internal=[{"source": "manual.md"}])
        assert collector.source_type == "internal"
        assert collector.sources == [{"source": "manual.md"}]

    def test_web_tiene_prioridad_sobre_interna(self):
        # Si hubo fallback, la fuente reportada es web aunque antes se haya
        # consultado la base interna
        collector = SourceCollector(
            internal=[{"source": "manual.md"}],
            web=[{"source": "Microsoft Learn", "url": "https://learn.microsoft.com"}],
        )
        assert collector.source_type == "web"
        assert collector.sources[0]["url"].startswith("https://")


class TestCreateMentorAgent:
    def test_construye_grafo_con_dos_tools(self, monkeypatch):
        settings_fake = dataclasses.replace(
            settings, openrouter_api_key="sk-or-test-fake"
        )
        monkeypatch.setattr("backend.llm.llm.settings", settings_fake)

        vs = create_vectorstore(
            [Document(page_content="Manual de prueba.", metadata={"source": "m.md"})],
            embeddings=FakeEmbeddings(),
        )
        agent, collector = create_mentor_agent(vectorstore=vs)

        assert agent is not None
        assert isinstance(collector, SourceCollector)
        # El grafo expone las dos herramientas registradas
        nombres_tools = set(agent.nodes["tools"].bound._tools_by_name.keys())
        assert nombres_tools == {"buscar_base_conocimiento", "buscar_en_web", "listar_documentos"}

    def test_system_prompt_define_reglas_clave(self):
        assert "buscar_base_conocimiento" in SYSTEM_PROMPT
        assert "buscar_en_web" in SYSTEM_PROMPT
        assert "listar_documentos" in SYSTEM_PROMPT
        assert "español o portugués" in SYSTEM_PROMPT
        assert "RELEVANCIA SUFICIENTE" in SYSTEM_PROMPT
        assert "RELEVANCIA INSUFICIENTE" in SYSTEM_PROMPT


class _FakeAgent:
    """Agente falso que simula una respuesta del LLM."""

    def invoke(self, payload):
        assert payload["messages"][-1]["content"]  # hay pregunta
        return {"messages": [AIMessage(content="Respuesta simulada del mentor.")]}


class TestAsk:
    def test_respuesta_con_fuente_interna(self, monkeypatch):
        collector = SourceCollector(internal=[{"source": "manual_red.md"}])
        monkeypatch.setattr(
            "backend.llm.agent.create_mentor_agent",
            lambda **kwargs: (_FakeAgent(), collector),
        )
        result = ask("¿cuál es la contraseña del wifi?")

        assert result["answer"] == "Respuesta simulada del mentor."
        assert result["source_type"] == "internal"
        assert result["sources"] == [{"source": "manual_red.md"}]

    def test_respuesta_con_fallback_web(self, monkeypatch):
        collector = SourceCollector(
            web=[{"source": "Microsoft Learn", "url": "https://learn.microsoft.com"}]
        )
        monkeypatch.setattr(
            "backend.llm.agent.create_mentor_agent",
            lambda **kwargs: (_FakeAgent(), collector),
        )
        result = ask("¿cómo configuro una VPN en Windows?")
        assert result["source_type"] == "web"

    def test_error_de_configuracion_es_controlado(self, monkeypatch):
        def _falla(**kwargs):
            raise RuntimeError("Configuración inválida: falta OPENROUTER_API_KEY")

        monkeypatch.setattr("backend.llm.agent.create_mentor_agent", _falla)
        result = ask("hola")
        assert result["source_type"] == "error"
        assert "⚠️" in result["answer"]

    def test_error_generico_es_controlado(self, monkeypatch):
        def _falla(**kwargs):
            raise ValueError("429 rate limit")

        monkeypatch.setattr("backend.llm.agent.create_mentor_agent", _falla)
        result = ask("hola")
        assert result["source_type"] == "error"
        assert "inténtalo de nuevo" in result["answer"]

    def test_bad_request_reintenta_y_mensaje_especifico(self, monkeypatch):
        from openai import BadRequestError

        llamadas = {"n": 0}

        def _factory(**kwargs):
            llamadas["n"] += 1
            if llamadas["n"] == 1:
                raise BadRequestError(
                    "tool_use_failed",
                    response=None,
                    body={"error": {"message": "Failed to call a function"}},
                )
            return _FakeAgent(), SourceCollector()

        monkeypatch.setattr("backend.llm.agent.create_mentor_agent", _factory)
        result = ask("pregunta")

        assert result["source_type"] != "error"
        assert llamadas["n"] == 2

    def test_reintenta_con_modelo_de_respaldo_ante_429(self, monkeypatch):
        llamadas = {"n": 0, "modelos": []}

        def _factory(**kwargs):
            llamadas["n"] += 1
            llamadas["modelos"].append(kwargs.get("model"))
            if llamadas["n"] == 1:
                raise ValueError("Error code: 429 - rate limited upstream")
            return _FakeAgent(), SourceCollector()

        monkeypatch.setattr("backend.llm.agent.create_mentor_agent", _factory)
        result = ask("pregunta de prueba")

        assert result["source_type"] != "error"
        assert llamadas["n"] == 2
        # El primer intento fue el modelo principal y el segundo el respaldo
        assert llamadas["modelos"][0] == settings.llm_model
        assert llamadas["modelos"][1] == settings.llm_fallback_models[0]
        assert result["model"] == settings.llm_fallback_models[0]

    def test_si_todos_los_modelos_estan_limitados_devuelve_error(self, monkeypatch):
        def _factory(**kwargs):
            raise ValueError("429 rate limit")

        monkeypatch.setattr("backend.llm.agent.create_mentor_agent", _factory)
        result = ask("pregunta")
        assert result["source_type"] == "error"
        assert "inténtalo de nuevo" in result["answer"]

    def test_historial_se_respeta(self, monkeypatch):
        capturado = {}

        class _AgenteEspia:
            def invoke(self, payload):
                capturado["messages"] = payload["messages"]
                return {"messages": [AIMessage(content="ok")]}

        monkeypatch.setattr(
            "backend.llm.agent.create_mentor_agent",
            lambda **kwargs: (_AgenteEspia(), SourceCollector()),
        )
        historial = [
            {"role": "user", "content": "hola"},
            {"role": "assistant", "content": "¡Hola! ¿En qué te ayudo?"},
        ]
        ask("siguiente pregunta", chat_history=historial)

        assert len(capturado["messages"]) == 3
        assert capturado["messages"][0]["content"] == "hola"
        assert capturado["messages"][-1]["content"] == "siguiente pregunta"

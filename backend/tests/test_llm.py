"""Tests del cliente LLM (OpenRouter). No se hacen llamadas de red."""

import dataclasses

import pytest

from backend.config.settings import settings
from backend.llm.llm import get_llm


def _settings_con_key():
    return dataclasses.replace(settings, openrouter_api_key="sk-or-test-fake")


class TestGetLlm:
    def test_falla_sin_api_key(self, monkeypatch):
        sin_key = dataclasses.replace(settings, openrouter_api_key="")
        monkeypatch.setattr("backend.llm.llm.settings", sin_key)
        with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
            get_llm()

    def test_construye_cliente_openrouter(self, monkeypatch):
        monkeypatch.setattr("backend.llm.llm.settings", _settings_con_key())
        llm = get_llm()

        assert llm.model_name == settings.llm_model
        assert str(llm.openai_api_base).rstrip("/") == settings.openrouter_base_url
        # La key queda protegida como SecretStr (no se expone en repr)
        assert "sk-or-test-fake" not in repr(llm)
        assert llm.temperature == settings.llm_temperature

    def test_permite_overrides(self, monkeypatch):
        monkeypatch.setattr("backend.llm.llm.settings", _settings_con_key())
        llm = get_llm(model="google/gemma-2-9b-it:free", temperature=0.7)
        assert llm.model_name == "google/gemma-2-9b-it:free"
        assert llm.temperature == 0.7


class TestSettingsValidate:
    def test_validate_detecta_falta_de_key(self):
        sin_key = dataclasses.replace(settings, openrouter_api_key="")
        assert any("OPENROUTER_API_KEY" in e for e in sin_key.validate())

    def test_validate_ok_con_key(self):
        assert _settings_con_key().validate() == []

"""Cliente LLM vía OpenRouter (endpoint compatible con OpenAI).

El LLM es REMOTO (nube): la VM local/OCI solo ejecuta los embeddings.
OpenRouter permite usar modelos gratuitos (sufijo `:free`) con rate limits
moderados, ideal para el challenge.

Documentación OpenRouter: https://openrouter.ai/docs
"""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from backend.config.settings import settings


def get_llm(**overrides) -> ChatOpenAI:
    """Construye el cliente LLM configurado para OpenRouter.

    Raises:
        RuntimeError: si falta la API key (fallo rápido al arrancar).
    """
    errors = settings.validate()
    if errors:
        raise RuntimeError("Configuración inválida: " + " | ".join(errors))

    params = {
        "model": settings.llm_model,
        "api_key": settings.openrouter_api_key,
        "base_url": settings.openrouter_base_url,
        "temperature": settings.llm_temperature,
        "timeout": 60,
        # Reintentos ante 429/timeouts típicos de los modelos :free
        "max_retries": 3,
        # Headers recomendados por OpenRouter (identificación de la app)
        "default_headers": {
            "X-Title": settings.app_name,
        },
    }
    params.update(overrides)
    return ChatOpenAI(**params)

"""Tests del caché de respuestas del chat."""

from __future__ import annotations

import time

from backend.common.cache import TTLCache


class TestTTLCache:
    def test_guarda_y_recupera_respuesta(self):
        cache = TTLCache(maxsize=10, ttl_seconds=60)
        cache.set("¿Cómo configuro la VPN?", "es", {"answer": "Usa Cisco AnyConnect"})

        cached = cache.get("¿Cómo configuro la VPN?", "es")
        assert cached == {"answer": "Usa Cisco AnyConnect"}

    def test_clave_es_case_insensitive_y_normaliza_espacios(self):
        cache = TTLCache(maxsize=10, ttl_seconds=60)
        cache.set("  CÓMO configuro LA vpn?  ", "es", {"answer": "ok"})

        assert cache.get("cómo configuro la vpn?", "es") == {"answer": "ok"}

    def test_idioma_es_parte_de_la_clave(self):
        cache = TTLCache(maxsize=10, ttl_seconds=60)
        cache.set("vpn", "es", {"answer": "español"})
        cache.set("vpn", "pt", {"answer": "português"})

        assert cache.get("vpn", "es") == {"answer": "español"}
        assert cache.get("vpn", "pt") == {"answer": "português"}

    def test_expira_tras_el_ttl(self):
        cache = TTLCache(maxsize=10, ttl_seconds=0.05)
        cache.set("pregunta", "es", {"answer": "ahora"})
        assert cache.get("pregunta", "es") is not None

        time.sleep(0.1)
        assert cache.get("pregunta", "es") is None

    def test_lru_evita_mas_alla_de_maxsize(self):
        cache = TTLCache(maxsize=2, ttl_seconds=60)
        cache.set("a", "es", 1)
        cache.set("b", "es", 2)
        cache.set("c", "es", 3)

        assert cache.get("a", "es") is None
        assert cache.get("b", "es") == 2
        assert cache.get("c", "es") == 3

    def test_clear_vacia_la_cache(self):
        cache = TTLCache(maxsize=10, ttl_seconds=60)
        cache.set("x", "es", 1)
        cache.clear()
        assert cache.get("x", "es") is None

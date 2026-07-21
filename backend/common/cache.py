"""Caché en memoria con TTL para respuestas del agente mentor.

Reduce llamadas repetidas al LLM cuando se repite la misma pregunta dentro
del tiempo de vida configurado. Es thread-safe y con límite de entradas.

Se invalida automáticamente al subir nuevos documentos desde /api/admin/upload
para evitar respuestas obsoletas ante cambios en la base de conocimiento.
"""

from __future__ import annotations

import hashlib
import os
import threading
import time
from collections import OrderedDict
from typing import Any


class TTLCache:
    """Caché thread-safe con expiración por tiempo y límite LRU de entradas."""

    def __init__(self, maxsize: int = 500, ttl_seconds: int = 600):
        self.maxsize = maxsize
        self.ttl = ttl_seconds
        self._data: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._lock = threading.RLock()

    def _key(self, question: str, lang: str = "es") -> str:
        """Clave determinista a partir de pregunta normalizada e idioma."""
        normalized = " ".join(question.strip().lower().split())
        payload = f"{normalized}|{lang}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, question: str, lang: str = "es") -> Any | None:
        """Recupera una respuesta cacheada si aún no expiró."""
        key = self._key(question, lang)
        with self._lock:
            self._cleanup()
            entry = self._data.get(key)
            if entry is None:
                return None
            if time.time() > entry["expires"]:
                self._data.pop(key, None)
                return None
            # Mover al final (más recientemente usado)
            self._data.move_to_end(key, last=True)
            return entry["value"]

    def set(self, question: str, lang: str = "es", value: Any = None) -> None:
        """Guarda una respuesta en caché con el TTL configurado."""
        key = self._key(question, lang)
        with self._lock:
            self._cleanup()
            # Evitar crecer más allá del límite (LRU)
            while len(self._data) >= self.maxsize and self._data:
                self._data.popitem(last=False)
            self._data[key] = {"value": value, "expires": time.time() + self.ttl}
            self._data.move_to_end(key, last=True)

    def clear(self) -> None:
        """Vacía la caché (útil tras ingestas de nuevos documentos)."""
        with self._lock:
            self._data.clear()

    def _cleanup(self) -> None:
        """Elimina entradas expiradas."""
        now = time.time()
        expired = [k for k, v in self._data.items() if now > v["expires"]]
        for k in expired:
            self._data.pop(k, None)


# Instancia global usada por la API
response_cache = TTLCache(
    maxsize=int(os.getenv("CACHE_MAXSIZE", "500")),
    ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "600")),
)

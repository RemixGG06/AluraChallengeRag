"""Smoke test end-to-end de MentorTI Nexus con LLM real (OpenRouter).

Para cada consulta de prueba muestra:
1. Scores de relevancia de la búsqueda interna (insumo de calibración KB-09).
2. La decisión real del agente (fuente interna vs. fallback web) y su respuesta.

Uso:
    python -m backend.scripts.smoke_e2e
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Consola Windows en UTF-8 (KB-07) + flush por línea para logs en vivo
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

from backend.config.settings import settings
from backend.llm.agent import ask
from backend.rag.vectorstore import load_vectorstore, search_with_scores

# (consulta, expectativa) — la expectativa es cualitativa, para lectura humana
QUERIES = [
    ("¿Cómo me conecto a la VPN de la empresa?", "internal"),
    ("¿Cuál es la política de contraseñas de la empresa?", "internal"),
    ("Como faço para conectar na VPN da empresa?", "internal"),  # PT cruzado
    ("¿Qué IP tiene el servidor de archivos?", "internal"),
    ("¿Cómo soluciono el error 0x80070005 de Windows Update?", "web"),
    ("Como corrijo o erro 0x80070005 do Windows Update?", "web"),  # PT web
]


def main() -> None:
    vectorstore = load_vectorstore()
    if vectorstore is None:
        print("No hay índice FAISS. Ejecuta python -m backend.scripts.ingest_samples primero.")
        sys.exit(1)

    print(f"Umbral configurado: {settings.score_threshold}")
    print(f"Modelo principal: {settings.llm_model}")
    print("=" * 78)

    aciertos = 0
    for i, (query, expected) in enumerate(QUERIES, start=1):
        print(f"\n[{i}/{len(QUERIES)}] {query}")
        print(f"    Expectativa: {expected}")

        # --- Calibración: scores crudos de la búsqueda interna ---
        results = search_with_scores(vectorstore, query, k=3)
        scores = ", ".join(
            f"{doc.metadata.get('source', '?')}={score:.3f}"
            for doc, score in results
        )
        print(f"    Scores internos: {scores}")

        # --- Decisión real del agente ---
        result = ask(query, vectorstore=vectorstore)
        source = result["source_type"]
        ok = "✅" if source == expected else "⚠️"
        if source == expected:
            aciertos += 1
        print(f"    {ok} Decisión del agente: {source} (modelo: "
              f"{result.get('model', 'n/a')})")
        answer = result["answer"].replace("\n", " ")
        print(f"    Respuesta: {answer[:220]}...")

        if i < len(QUERIES):
            time.sleep(3)  # cortesía ante rate limits de los modelos :free

    print("\n" + "=" * 78)
    print(f"RESULTADO: {aciertos}/{len(QUERIES)} decisiones correctas")


if __name__ == "__main__":
    main()

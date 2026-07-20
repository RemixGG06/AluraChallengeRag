"""Ingsta los documentos de prueba (data/samples/) en el índice FAISS real.

Uso:
    python -m backend.scripts.generate_samples   # primero generar
    python -m backend.scripts.ingest_samples     # luego ingestar
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.rag.vectorstore import ingest_file, list_indexed_sources

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "samples"

# Mapeo documento -> departamento (cobertura de dominios del challenge)
DOCUMENTS = {
    "manual_vpn_red.md": "operaciones",
    "normativa_seguridad_ti.docx": "rh",
    "inventario_equipos.xlsx": "sistemas",
    "contactos_soporte.csv": "sistemas",
    "procedimiento_backups.html": "operaciones",
    "guia_onboarding.pdf": "rh",
}


def main() -> None:
    for name, department in DOCUMENTS.items():
        path = SAMPLES_DIR / name
        if not path.exists():
            print(f"  [FALTA] {name} (ejecuta python -m backend.scripts.generate_samples)")
            continue
        chunks = ingest_file(path, department=department)
        print(f"  [OK] {name} ({department}): {chunks} chunks")

    print("\nINVENTARIO DEL ÍNDICE:")
    for item in list_indexed_sources():
        print(
            f"  - {item['source']} | depto: {item['department']} | "
            f"{item['chunks']} chunks"
        )


if __name__ == "__main__":
    main()

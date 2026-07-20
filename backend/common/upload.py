"""Utilidad de guardado seguro de archivos subidos por el usuario.

Migrada desde frontend/views/admin_view.py (Streamlit) para que el backend
la exponga vía API sin depender de ninguna UI.
"""

from __future__ import annotations

from pathlib import Path

from backend.rag.loaders.document_loader import SUPPORTED_EXTENSIONS


class UploadedFile:
    """Interfaz mínima para un archivo subido (compatible con FastAPI UploadFile)."""

    def __init__(self, name: str, content: bytes):
        self.name = name
        self._content = content

    def getbuffer(self):
        return memoryview(self._content)


def save_uploaded_file(uploaded_file, dest_dir: str | Path) -> Path:
    """Guarda un archivo subido en disco de forma segura.

    - Sanitiza el nombre (anti path traversal: ``../x.pdf`` -> ``x.pdf``).
    - Valida la extensión contra los formatos soportados.

    Raises:
        ValueError: si la extensión no está soportada.
    """
    name = Path(uploaded_file.name).name
    extension = Path(name).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato no soportado: '{extension}'")

    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / name
    dest.write_bytes(uploaded_file.getbuffer())
    return dest

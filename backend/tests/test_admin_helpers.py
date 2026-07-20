"""Tests de los helpers de upload (guardado seguro de archivos).

Migrado desde frontend/ (Streamlit) a core/upload.py.
"""

import pytest

from backend.common.upload import save_uploaded_file


class _FakeUploadedFile:
    """Simula un archivo subido para tests (name + contenido por defecto)."""
    def __init__(self, name: str, content: bytes = b"contenido"):
        self.name = name
        self._content = content
    def getbuffer(self):
        return memoryview(self._content)


class TestSaveUploadedFile:
    def test_guarda_archivo_valido(self, tmp_path):
        dest = save_uploaded_file(_FakeUploadedFile("manual.md"), tmp_path)
        assert dest == tmp_path / "manual.md"
        assert dest.read_bytes() == b"contenido"

    def test_sanitiza_path_traversal(self, tmp_path):
        dest = save_uploaded_file(_FakeUploadedFile("../../evil.md"), tmp_path)
        # El nombre queda reducido a 'evil.md' y dentro del destino
        assert dest.name == "evil.md"
        assert dest.parent == tmp_path
        assert dest.exists()

    def test_rechaza_extension_no_soportada(self, tmp_path):
        with pytest.raises(ValueError, match="Formato no soportado"):
            save_uploaded_file(_FakeUploadedFile("virus.exe"), tmp_path)

    def test_crea_directorio_si_no_existe(self, tmp_path):
        dest_dir = tmp_path / "nueva" / "ruta"
        dest = save_uploaded_file(_FakeUploadedFile("doc.csv"), dest_dir)
        assert dest.exists()

"""Tests del sistema de internacionalización (es/pt)."""

import pytest

from backend.config.i18n import (
    DEFAULT_LANG,
    DEPARTMENTS,
    SUPPORTED_LANGS,
    TRANSLATIONS,
    t,
)


class TestCatalogos:
    def test_ambos_idiomas_tienen_las_mismas_claves(self):
        claves_es = set(TRANSLATIONS["es"].keys())
        claves_pt = set(TRANSLATIONS["pt"].keys())
        assert claves_es == claves_pt, (
            f"Faltan claves. Solo en es: {claves_es - claves_pt}. "
            f"Solo en pt: {claves_pt - claves_es}"
        )

    def test_sin_traducciones_vacias(self):
        for lang, catalog in TRANSLATIONS.items():
            for key, value in catalog.items():
                assert value.strip(), f"Traducción vacía: {lang}.{key}"

    def test_todos_los_departamentos_son_traducibles(self):
        for lang in SUPPORTED_LANGS:
            for dept in DEPARTMENTS:
                traducido = t(f"dept_{dept}", lang)
                assert traducido != f"dept_{dept}"


class TestFuncionT:
    def test_traduce_espanol(self):
        assert t("mode_admin", "es") == "Administrador"

    def test_traduce_portugues(self):
        assert t("mode_admin", "pt") == "Administrador"
        assert "Busca na web" in t("badge_web", "pt")

    def test_idioma_desconocido_cae_a_default(self):
        assert t("mode_admin", "fr") == t("mode_admin", DEFAULT_LANG)

    def test_clave_desconocida_devuelve_la_clave(self):
        assert t("clave_que_no_existe", "es") == "clave_que_no_existe"

    def test_placeholders_presentes_en_ambos_idiomas(self):
        for lang in SUPPORTED_LANGS:
            assert "{name}" in t("admin_success", lang)
            assert "{chunks}" in t("admin_success", lang)
            assert "{error}" in t("admin_error", lang)

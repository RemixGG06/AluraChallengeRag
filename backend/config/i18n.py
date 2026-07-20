"""Internacionalización (i18n) de MentorTI Nexus — catálogo backend.

Este módulo contiene el catálogo de traducciones es/pt usado por el backend
(API) y los tests. El frontend React tiene su propio catálogo en JSON
/frontend/src/i18n/es.json y pt.json (migrado desde este código).

El catálogo es ADITIVO: las claves existentes no se renombran ni eliminan;
las nuevas se agregan siempre en ambos idiomas a la vez.
"""

from __future__ import annotations

SUPPORTED_LANGS = ("es", "pt")
DEFAULT_LANG = "es"

DEPARTMENTS = ("general", "rh", "operaciones", "sistemas")

TRANSLATIONS: dict[str, dict[str, str]] = {
    "es": {
        "app_caption": "Mentor técnico 24/7 para el onboarding de practicantes de TI",
        "sidebar_title": "Configuración",
        "language": "Idioma",
        "mode": "Modo de vista",
        "mode_user": "Usuario (Chat)",
        "mode_admin": "Administrador",
        "theme_light": "☀️ Tema claro",
        "theme_dark": "🌙 Tema oscuro",
        "sidebar_toggle": "Mostrar / ocultar menú lateral",
        "sources_show": "📄 Fuentes",
        "sources_hide": "✕ Cerrar fuentes",
        "tab_chat": "Chat",
        "tab_admin": "Administración",
        "tab_about": "Acerca de",
        "footer_model": "Modelo activo",
        "footer_messages": "mensajes en esta sesión",
        "chat_title": "Asistente de onboarding",
        "chat_welcome": (
            "¡Hola! Soy tu mentor técnico. Pregúntame sobre manuales, "
            "credenciales, redes o procedimientos de la empresa."
        ),
        "chat_input_placeholder": "Escribe tu duda técnica aquí…",
        "thinking": "Consultando manuales y fuentes…",
        "badge_internal": "Fuente: Documento interno",
        "badge_web": "Fuente: Búsqueda web",
        "badge_assistant": "Respuesta directa del asistente",
        "badge_error": "Se produjo un error",
        "sources_expander": "Ver fuentes utilizadas",
        "source_relevance": "relevancia",
        "sources_panel_title": "Fuentes consultadas",
        "confidence_label": "Confianza (relevancia semántica)",
        "trusted_label": "Fuente confiable ✅",
        "untrusted_label": "Fuente no verificada ⚠️",
        "no_sources_yet": "Aún no se han consultado fuentes. Haz una pregunta técnica.",
        "clear_chat": "Limpiar conversación",
        "admin_title": "Panel de administración",
        "admin_upload_label": "Arrastra y suelta los manuales (PDF, Word, Excel, CSV, Markdown, HTML, TXT)",
        "admin_department": "Departamento del documento",
        "admin_index_button": "Indexar documentos",
        "admin_no_files": "Primero selecciona al menos un archivo.",
        "admin_success": "{name}: {chunks} fragmentos indexados.",
        "admin_error": "{name}: {error}",
        "admin_inventory_title": "Inventario de documentos vectorizados",
        "admin_empty_inventory": "Aún no hay documentos indexados. Sube el primero arriba.",
        "col_source": "Documento",
        "col_department": "Departamento",
        "col_chunks": "Fragmentos",
        "admin_subtab_upload": "Subir documentos",
        "admin_subtab_inventory": "Inventario",
        "admin_upload_formats": "Formatos aceptados: {formats}",
        "admin_stat_documents": "Documentos",
        "admin_stat_chunks": "Fragmentos totales",
        "admin_stat_departments": "Departamentos",
        "about_title": "Acerca de MentorTI Nexus",
        "about_purpose_title": "Propósito",
        "about_purpose_body": (
            "Sistema de capacitación y autoaprendizaje basado en IA (Agentic "
            "RAG) que acelera el onboarding de practicantes de TI respondiendo "
            "dudas técnicas con los manuales internos y, si no bastan, con "
            "búsqueda web en fuentes confiables."
        ),
        "about_models_title": "Modelos de lenguaje",
        "about_llm": "Modelo principal",
        "about_fallbacks": "Modelos de respaldo",
        "about_temperature": "Temperatura",
        "about_embeddings": "Modelo de embeddings",
        "about_device": "Dispositivo",
        "about_retrieval_title": "Recuperación (RAG)",
        "about_k": "Fragmentos por consulta (k)",
        "about_threshold": "Umbral de relevancia",
        "about_departments_title": "Departamentos cubiertos",
        "about_formats_title": "Formatos de documento",
        "about_languages_title": "Idiomas de la interfaz",
        "about_datastore_title": "Almacenamiento",
        "about_index_path": "Índice vectorial FAISS",
        "about_raw_path": "Documentos originales",
        "dept_general": "General",
        "dept_rh": "Recursos Humanos",
        "dept_operaciones": "Operaciones",
        "dept_sistemas": "Sistemas",
    },
    "pt": {
        "app_caption": "Mentor técnico 24/7 para o onboarding de estagiários de TI",
        "sidebar_title": "Configurações",
        "language": "Idioma",
        "mode": "Modo de visualização",
        "mode_user": "Usuário (Chat)",
        "mode_admin": "Administrador",
        "theme_light": "☀️ Tema claro",
        "theme_dark": "🌙 Tema escuro",
        "sidebar_toggle": "Mostrar / ocultar menu lateral",
        "sources_show": "📄 Fontes",
        "sources_hide": "✕ Fechar fontes",
        "tab_chat": "Chat",
        "tab_admin": "Administração",
        "tab_about": "Sobre",
        "footer_model": "Modelo ativo",
        "footer_messages": "mensagens nesta sessão",
        "chat_title": "Assistente de onboarding",
        "chat_welcome": (
            "Olá! Sou seu mentor técnico. Pergunte-me sobre manuais, "
            "credenciais, redes ou procedimentos da empresa."
        ),
        "chat_input_placeholder": "Digite sua dúvida técnica aqui…",
        "thinking": "Consultando manuais e fontes…",
        "badge_internal": "Fonte: Documento interno",
        "badge_web": "Fonte: Busca na web",
        "badge_assistant": "Resposta direta do assistente",
        "badge_error": "Ocorreu um erro",
        "sources_expander": "Ver fontes utilizadas",
        "source_relevance": "relevância",
        "sources_panel_title": "Fontes consultadas",
        "confidence_label": "Confiança (relevância semântica)",
        "trusted_label": "Fonte confiável ✅",
        "untrusted_label": "Fonte não verificada ⚠️",
        "no_sources_yet": "Ainda não foram consultadas fontes. Faça uma pergunta técnica.",
        "clear_chat": "Limpar conversa",
        "admin_title": "Painel de administração",
        "admin_upload_label": "Arraste e solte os manuais (PDF, Word, Excel, CSV, Markdown, HTML, TXT)",
        "admin_department": "Departamento do documento",
        "admin_index_button": "Indexar documentos",
        "admin_no_files": "Selecione pelo menos um arquivo primeiro.",
        "admin_success": "{name}: {chunks} fragmentos indexados.",
        "admin_error": "{name}: {error}",
        "admin_inventory_title": "Inventário de documentos vetorizados",
        "admin_empty_inventory": "Ainda não há documentos indexados. Envie o primeiro acima.",
        "col_source": "Documento",
        "col_department": "Departamento",
        "col_chunks": "Fragmentos",
        "admin_subtab_upload": "Enviar documentos",
        "admin_subtab_inventory": "Inventário",
        "admin_upload_formats": "Formatos aceitos: {formats}",
        "admin_stat_documents": "Documentos",
        "admin_stat_chunks": "Fragmentos totais",
        "admin_stat_departments": "Departamentos",
        "about_title": "Sobre o MentorTI Nexus",
        "about_purpose_title": "Propósito",
        "about_purpose_body": (
            "Sistema de capacitação e autoaprendizagem baseado em IA (Agentic "
            "RAG) que acelera o onboarding de estagiários de TI respondendo "
            "dúvidas técnicas com os manuais internos e, se não bastarem, com "
            "busca na web em fontes confiáveis."
        ),
        "about_models_title": "Modelos de linguagem",
        "about_llm": "Modelo principal",
        "about_fallbacks": "Modelos de reserva",
        "about_temperature": "Temperatura",
        "about_embeddings": "Modelo de embeddings",
        "about_device": "Dispositivo",
        "about_retrieval_title": "Recuperação (RAG)",
        "about_k": "Fragmentos por consulta (k)",
        "about_threshold": "Limite de relevância",
        "about_departments_title": "Departamentos cobertos",
        "about_formats_title": "Formatos de documento",
        "about_languages_title": "Idiomas da interface",
        "about_datastore_title": "Armazenamento",
        "about_index_path": "Índice vetorial FAISS",
        "about_raw_path": "Documentos originais",
        "dept_general": "Geral",
        "dept_rh": "Recursos Humanos",
        "dept_operaciones": "Operações",
        "dept_sistemas": "Sistemas",
    },
}


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    """Traduce una clave al idioma pedido.

    Fallback: idioma desconocido -> español; clave desconocida -> la propia clave.
    """
    catalog = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANG])
    return catalog.get(key, TRANSLATIONS[DEFAULT_LANG].get(key, key))

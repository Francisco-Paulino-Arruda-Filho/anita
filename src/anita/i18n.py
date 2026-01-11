import json
import os
import locale

TRANSLATIONS_PATH = os.path.join(os.path.dirname(__file__), 'anita_strings.json')

with open(TRANSLATIONS_PATH, encoding='utf-8') as f:
    TRANSLATIONS = json.load(f)


def _detect_system_lang() -> str:
    """
    Tenta descobrir o idioma padrão do sistema e devolve código curto ("pt", "en", ...).
    Se não conseguir detectar, retorna "pt" como padrão.
    """
    try:
        lang_code, _ = locale.getdefaultlocale()  # e.g. "pt_BR", "en_US"
    except Exception:
        lang_code = None

    if not lang_code:
        return 'pt'

    short = lang_code.split('_', 1)[0].lower()
    if short in ('pt', 'en'):
        return short

    return 'pt'


def t(key: str, lang: str | None = None) -> str:
    """
    Retorna a string traduzida para a chave e idioma informados.
    key: identificador da mensagem (ex.: 'BTN_VERIFY')
    lang: código do idioma (ex.: 'pt', 'en'). Se None, usa idioma padrão do sistema.
    """
    if lang is None:
        lang = _detect_system_lang()

    entry = TRANSLATIONS.get(key, {})

    # Formato esperado: { "KEY": { "pt": "...", "en": "..." } }
    if isinstance(entry, dict):
        # tenta idioma detectado/pedido, depois pt como default; se nada existir, devolve a própria key
        return entry.get(lang, entry.get('pt', key))

    # fallback para caso alguma entrada ainda seja string simples
    return str(entry) if entry else key

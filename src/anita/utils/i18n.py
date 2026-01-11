import json
import os
from dotenv import load_dotenv

load_dotenv()

TRANSLATIONS_PATH = os.path.join(os.path.dirname(__file__), 'anita_strings.json')

with open(TRANSLATIONS_PATH, encoding='utf-8') as f:
    TRANSLATIONS = json.load(f)


def t(key: str, lang: str | None = None) -> str:
    """
    Retorna a string traduzida para a chave e idioma informados.
    key: identificador da mensagem (ex.: 'BTN_VERIFY')
    lang: código do idioma (ex.: 'pt', 'en'). Se None, usa a variável de ambiente ANITA_LANG ou 'pt' como padrão.
    """
    if lang is None:
        lang = os.getenv('ANITA_LANG', 'pt')

    entry = TRANSLATIONS.get(key, {})

    # Formato esperado: { "KEY": { "pt": "...", "en": "..." } }
    if isinstance(entry, dict):
        # tenta idioma detectado/pedido, depois pt como default; se nada existir, devolve a própria key
        return entry.get(lang, entry.get('pt', key))

    # fallback para caso alguma entrada ainda seja string simples
    return str(entry) if entry else key

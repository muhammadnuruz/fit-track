from __future__ import annotations

from app.i18n.languages import DEFAULT_LANG, Lang
from app.i18n.translations import en, ru, uz

CATALOG: dict[Lang, dict[str, str]] = {
    Lang.UZ: uz.MESSAGES,
    Lang.RU: ru.MESSAGES,
    Lang.EN: en.MESSAGES,
}


def t(key: str, lang: Lang = DEFAULT_LANG, /, **kwargs: object) -> str:
    catalog = CATALOG.get(lang, CATALOG[DEFAULT_LANG])
    template = catalog.get(key) or CATALOG[DEFAULT_LANG].get(key) or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template


def missing_keys() -> dict[Lang, set[str]]:
    all_keys: set[str] = set()
    for messages in CATALOG.values():
        all_keys |= messages.keys()
    return {lang: all_keys - set(messages) for lang, messages in CATALOG.items()}

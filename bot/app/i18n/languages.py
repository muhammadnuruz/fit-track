from __future__ import annotations

import enum
from dataclasses import dataclass


class Lang(str, enum.Enum):
    UZ = "uz"
    RU = "ru"
    EN = "en"


@dataclass(frozen=True, slots=True)
class LanguageInfo:
    code: Lang
    native_name: str
    flag: str


LANGUAGES: tuple[LanguageInfo, ...] = (
    LanguageInfo(Lang.UZ, "O'zbekcha", "🇺🇿"),
    LanguageInfo(Lang.RU, "Русский", "🇷🇺"),
    LanguageInfo(Lang.EN, "English", "🇬🇧"),
)

DEFAULT_LANG: Lang = Lang.UZ

_BY_CODE: dict[str, Lang] = {lang.code.value: lang.code for lang in LANGUAGES}


def parse_lang(value: str | None) -> Lang:
    if value is None:
        return DEFAULT_LANG
    return _BY_CODE.get(value, DEFAULT_LANG)


def is_supported(value: str | None) -> bool:
    return value in _BY_CODE

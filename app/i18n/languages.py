"""Qo'llab-quvvatlanadigan tillar ro'yxati va metadatasi.

Yangi til qo'shish uchun (masalan qozoqcha):
  1) Bu yerga `Lang.KK = "kk"` va LANGUAGES ga bitta qator qo'shing.
  2) `app/i18n/translations/kk.py` faylida MESSAGES dict yozing.
  3) `app/i18n/catalog.py` dagi CATALOG ga import qo'shing.
Boshqa hech narsa o'zgartirish shart emas.
"""

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
    native_name: str  # o'z tilida yozilgan nom (tugmada ko'rinadi)
    flag: str


# Tanlov tugmalari shu tartibda ko'rsatiladi.
LANGUAGES: tuple[LanguageInfo, ...] = (
    LanguageInfo(Lang.UZ, "O'zbekcha", "🇺🇿"),
    LanguageInfo(Lang.RU, "Русский", "🇷🇺"),
    LanguageInfo(Lang.EN, "English", "🇬🇧"),
)

# Til tanlanmaganda / kalit topilmaganda ishlatiladigan zaxira til.
DEFAULT_LANG: Lang = Lang.UZ

_BY_CODE: dict[str, Lang] = {lang.code.value: lang.code for lang in LANGUAGES}


def parse_lang(value: str | None) -> Lang:
    """Matn ('uz') ni Lang ga o'giradi; noma'lum bo'lsa DEFAULT_LANG qaytaradi."""
    if value is None:
        return DEFAULT_LANG
    return _BY_CODE.get(value, DEFAULT_LANG)


def is_supported(value: str | None) -> bool:
    return value in _BY_CODE

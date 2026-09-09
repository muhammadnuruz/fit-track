from __future__ import annotations

import pytest

from app.i18n import (
    CATALOG,
    DEFAULT_LANG,
    LANGUAGES,
    Lang,
    is_supported,
    missing_keys,
    parse_lang,
    t,
)


def test_all_languages_have_catalog() -> None:
    for info in LANGUAGES:
        assert info.code in CATALOG, f"{info.code} uchun katalog yo'q"


def test_no_missing_keys_across_languages() -> None:
    missing = missing_keys()
    for lang, keys in missing.items():
        assert not keys, f"{lang.value} tilida yetishmayotgan kalitlar: {keys}"


def test_t_returns_correct_language() -> None:
    assert "xush kelibsiz" in t("start_welcome", Lang.UZ).lower()
    assert "добро пожаловать" in t("start_welcome", Lang.RU).lower()
    assert "welcome" in t("start_welcome", Lang.EN).lower()


def test_t_fallback_to_default_for_unknown_key() -> None:
    assert t("___yoq___", Lang.EN) == "___yoq___"


def test_t_default_lang_argument() -> None:
    assert t("help_text") == t("help_text", DEFAULT_LANG)


def test_t_format_kwargs_safe() -> None:
    assert t("help_text", Lang.UZ, unused="x")


@pytest.mark.parametrize(
    ("value", "expected"),
    [("uz", Lang.UZ), ("ru", Lang.RU), ("en", Lang.EN), (None, DEFAULT_LANG), ("de", DEFAULT_LANG)],
)
def test_parse_lang(value: str | None, expected: Lang) -> None:
    assert parse_lang(value) == expected


def test_is_supported() -> None:
    assert is_supported("uz")
    assert not is_supported("de")
    assert not is_supported(None)

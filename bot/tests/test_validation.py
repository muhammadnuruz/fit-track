import pytest

from app.validation import parse_age, parse_name, parse_number


@pytest.mark.parametrize("raw", ["Ali", "Mirzo Ulug'bek", "Анна", "Jean-Luc"])
def test_valid_names(raw: str) -> None:
    assert parse_name(raw) == raw


@pytest.mark.parametrize("raw", ["", "A", "R2D2", "Ali!"])
def test_invalid_names(raw: str) -> None:
    assert parse_name(raw) is None


def test_name_is_trimmed() -> None:
    assert parse_name("  Ali  ") == "Ali"


def test_number_accepts_comma_decimal() -> None:
    assert parse_number("82,5", 30, 350) == 82.5


def test_number_out_of_range_is_rejected() -> None:
    assert parse_number("20", 30, 350) is None


def test_number_text_is_rejected() -> None:
    assert parse_number("abc", 30, 350) is None


def test_age_must_be_integer_in_range() -> None:
    assert parse_age("28") == 28
    assert parse_age("28.5") is None
    assert parse_age("9") is None

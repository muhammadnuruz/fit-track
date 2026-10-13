import re

NAME_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё'\- ]+$")


def parse_name(raw: str) -> str | None:
    cleaned = raw.strip()
    if len(cleaned) < 2 or not NAME_PATTERN.fullmatch(cleaned):
        return None
    return cleaned


def parse_number(raw: str, low: float, high: float) -> float | None:
    try:
        value = float(raw.strip().replace(",", "."))
    except ValueError:
        return None
    if not low <= value <= high:
        return None
    return value


def parse_age(raw: str) -> int | None:
    value = parse_number(raw, 10, 100)
    return int(value) if value is not None and value.is_integer() else None

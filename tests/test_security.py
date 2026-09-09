from __future__ import annotations

import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

from app.api.security import InitDataError, validate_init_data

TOKEN = "123456:TEST-TOKEN"


def _build_init_data(user: dict, auth_date: int, token: str = TOKEN) -> str:
    pairs = {"auth_date": str(auth_date), "user": json.dumps(user, separators=(",", ":"))}
    data_check_string = "\n".join(f"{k}={pairs[k]}" for k in sorted(pairs))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    pairs["hash"] = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(pairs)


def test_valid_init_data() -> None:
    init = validate_init_data(
        _build_init_data({"id": 42, "language_code": "uz"}, int(time.time())), TOKEN
    )
    assert init.user_id == 42
    assert init.language_code == "uz"


def test_tampered_hash_rejected() -> None:
    raw = _build_init_data({"id": 42}, int(time.time()))
    tampered = raw.replace("id%22%3A42", "id%22%3A43")
    with pytest.raises(InitDataError):
        validate_init_data(tampered, TOKEN)


def test_wrong_token_rejected() -> None:
    raw = _build_init_data({"id": 42}, int(time.time()), token="999:OTHER")
    with pytest.raises(InitDataError):
        validate_init_data(raw, TOKEN)


def test_missing_hash_rejected() -> None:
    with pytest.raises(InitDataError):
        validate_init_data("auth_date=1&user=%7B%22id%22%3A1%7D", TOKEN)


def test_expired_init_data_rejected() -> None:
    raw = _build_init_data({"id": 42}, int(time.time()) - 100_000)
    with pytest.raises(InitDataError):
        validate_init_data(raw, TOKEN)


def test_empty_init_data_rejected() -> None:
    with pytest.raises(InitDataError):
        validate_init_data("", TOKEN)

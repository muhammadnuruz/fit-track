from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl


class InitDataError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class InitData:
    user_id: int
    language_code: str | None
    auth_date: int


def validate_init_data(init_data: str, bot_token: str, *, max_age_seconds: int = 86400) -> InitData:
    if not init_data:
        raise InitDataError("init_data bo'sh")
    if not bot_token:
        raise InitDataError("bot_token o'rnatilmagan")

    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise InitDataError("hash topilmadi")

    data_check_string = "\n".join(f"{key}={pairs[key]}" for key in sorted(pairs))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed, received_hash):
        raise InitDataError("imzo mos kelmadi")

    auth_date_raw = pairs.get("auth_date", "")
    if not auth_date_raw.isdigit():
        raise InitDataError("auth_date noto'g'ri")
    auth_date = int(auth_date_raw)
    if max_age_seconds > 0 and time.time() - auth_date > max_age_seconds:
        raise InitDataError("init_data eskirgan")

    user_raw = pairs.get("user")
    if not user_raw:
        raise InitDataError("user topilmadi")
    try:
        user = json.loads(user_raw)
    except json.JSONDecodeError as exc:
        raise InitDataError("user JSON buzuq") from exc

    user_id = user.get("id")
    if not isinstance(user_id, int):
        raise InitDataError("user id yo'q")

    return InitData(
        user_id=user_id,
        language_code=user.get("language_code"),
        auth_date=auth_date,
    )

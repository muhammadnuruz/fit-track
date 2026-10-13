import json

import httpx
import pytest

from app.api_client import ApiClient, ApiError, ProfileInput
from app.i18n import Lang

PROFILE_JSON = {
    "name": "Ali",
    "gender": "male",
    "age": 28,
    "height_cm": 178.0,
    "weight_kg": 82.0,
    "activity": "moderate",
    "goal": "bulk",
    "plan": {
        "bmr": 1800.0,
        "tdee": 2790.0,
        "target_kcal": 3125.0,
        "bmi": 25.9,
        "macros": {"kcal": 3125.0, "protein_g": 147.6, "carb_g": 380.0, "fat_g": 74.0},
    },
}


def _client(handler: httpx.MockTransport | None = None) -> ApiClient:
    return ApiClient("http://api.test", "secret", transport=handler)


async def test_sends_api_key_and_parses_profile() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["key"] = request.headers["X-API-Key"]
        seen["path"] = request.url.path
        return httpx.Response(200, json=PROFILE_JSON)

    client = _client(httpx.MockTransport(handler))
    profile = await client.get_profile(42)
    await client.close()

    assert seen == {"key": "secret", "path": "/api/v1/users/42/profile"}
    assert profile is not None
    assert profile.plan is not None
    assert profile.plan.macros.protein_g == 147.6


async def test_missing_profile_returns_none() -> None:
    client = _client(httpx.MockTransport(lambda _: httpx.Response(404, json={"detail": "x"})))
    assert await client.get_profile(42) is None
    await client.close()


async def test_server_error_raises_api_error() -> None:
    client = _client(httpx.MockTransport(lambda _: httpx.Response(500)))
    with pytest.raises(ApiError):
        await client.get_profile(42)
    await client.close()


async def test_unreachable_api_raises_api_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    client = _client(httpx.MockTransport(handler))
    with pytest.raises(ApiError):
        await client.get_language(42)
    await client.close()


async def test_upsert_profile_sends_body() -> None:
    sent: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        sent["method"] = request.method
        sent["body"] = json.loads(request.content)
        return httpx.Response(200, json=PROFILE_JSON)

    client = _client(httpx.MockTransport(handler))
    profile_input = ProfileInput(
        name="Ali",
        gender="male",
        age=28,
        height_cm=178.0,
        weight_kg=82.0,
        activity="moderate",
        goal="bulk",
    )
    await client.upsert_profile(42, profile_input)
    await client.close()

    assert sent["method"] == "PUT"
    assert sent["body"] == profile_input.to_json()


async def test_language_roundtrip() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(404)
        return httpx.Response(200, json={"language": "ru"})

    client = _client(httpx.MockTransport(handler))
    assert await client.get_language(42) is None
    assert await client.set_language(42, Lang.RU) == Lang.RU
    await client.close()


async def test_delete_user_reports_result() -> None:
    client = _client(httpx.MockTransport(lambda _: httpx.Response(204)))
    assert await client.delete_user(42) is True
    await client.close()

    client = _client(httpx.MockTransport(lambda _: httpx.Response(404)))
    assert await client.delete_user(42) is False
    await client.close()

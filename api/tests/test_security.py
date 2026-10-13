from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_requests_without_api_key_are_rejected() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/users/42/profile")
    assert response.status_code == 401


async def test_requests_with_wrong_api_key_are_rejected() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": "wrong"},
    ) as client:
        response = await client.get("/api/v1/users/42/profile")
    assert response.status_code == 401

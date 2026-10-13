from httpx import AsyncClient

PROFILE = {
    "name": "Ali Karimov",
    "gender": "male",
    "age": 28,
    "height_cm": 178,
    "weight_kg": 82,
    "activity": "moderate",
    "goal": "bulk",
}


async def test_put_profile_returns_plan(client: AsyncClient) -> None:
    response = await client.put("/api/v1/users/42/profile", json=PROFILE)
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Ali Karimov"
    assert body["weight_kg"] == 82
    assert body["plan"]["target_kcal"] > body["plan"]["tdee"] * 0.9
    assert body["plan"]["macros"]["protein_g"] > 0


async def test_get_profile_returns_saved_profile(client: AsyncClient) -> None:
    await client.put("/api/v1/users/42/profile", json=PROFILE)
    response = await client.get("/api/v1/users/42/profile")
    assert response.status_code == 200
    assert response.json()["goal"] == "bulk"


async def test_get_unknown_profile_is_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/999/profile")
    assert response.status_code == 404


async def test_second_put_same_day_updates_weight(client: AsyncClient) -> None:
    await client.put("/api/v1/users/42/profile", json=PROFILE)
    await client.put("/api/v1/users/42/profile", json={**PROFILE, "weight_kg": 80.5})
    body = (await client.get("/api/v1/users/42/profile")).json()
    assert body["weight_kg"] == 80.5


async def test_invalid_name_is_rejected(client: AsyncClient) -> None:
    response = await client.put("/api/v1/users/42/profile", json={**PROFILE, "name": "R2D2"})
    assert response.status_code == 422


async def test_out_of_range_age_is_rejected(client: AsyncClient) -> None:
    response = await client.put("/api/v1/users/42/profile", json={**PROFILE, "age": 5})
    assert response.status_code == 422


async def test_language_roundtrip(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/users/42/language")).status_code == 404
    response = await client.put("/api/v1/users/42/language", json={"language": "en"})
    assert response.json() == {"language": "en"}
    assert (await client.get("/api/v1/users/42/language")).json() == {"language": "en"}


async def test_invalid_language_is_rejected(client: AsyncClient) -> None:
    response = await client.put("/api/v1/users/42/language", json={"language": "de"})
    assert response.status_code == 422


async def test_stats_count_users_and_languages(client: AsyncClient) -> None:
    await client.put("/api/v1/users/42/profile", json=PROFILE)
    await client.put("/api/v1/users/42/language", json={"language": "en"})
    await client.put("/api/v1/users/7/language", json={"language": "ru"})
    body = (await client.get("/api/v1/admin/stats")).json()
    assert body["total_users"] == 2
    assert body["profiles"] == 1
    assert body["by_language"] == {"uz": 0, "ru": 1, "en": 1}


async def test_telegram_ids_lists_language_users(client: AsyncClient) -> None:
    await client.put("/api/v1/users/42/language", json={"language": "uz"})
    await client.put("/api/v1/users/7/language", json={"language": "ru"})
    body = (await client.get("/api/v1/admin/telegram-ids")).json()
    assert sorted(body["telegram_ids"]) == [7, 42]


async def test_delete_user_removes_profile_and_language(client: AsyncClient) -> None:
    await client.put("/api/v1/users/42/profile", json=PROFILE)
    await client.put("/api/v1/users/42/language", json={"language": "en"})
    assert (await client.delete("/api/v1/admin/users/42")).status_code == 204
    assert (await client.get("/api/v1/users/42/profile")).status_code == 404
    assert (await client.delete("/api/v1/admin/users/42")).status_code == 404

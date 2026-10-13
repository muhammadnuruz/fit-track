from dataclasses import dataclass
from typing import Any

import httpx

from app.i18n import Lang


class ApiError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class Macros:
    kcal: float
    protein_g: float
    carb_g: float
    fat_g: float


@dataclass(frozen=True, slots=True)
class Plan:
    bmr: float
    tdee: float
    target_kcal: float
    bmi: float
    macros: Macros


@dataclass(frozen=True, slots=True)
class Profile:
    name: str
    gender: str
    age: int
    height_cm: float
    weight_kg: float | None
    activity: str
    goal: str
    plan: Plan | None


@dataclass(frozen=True, slots=True)
class ProfileInput:
    name: str
    gender: str
    age: int
    height_cm: float
    weight_kg: float
    activity: str
    goal: str

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "activity": self.activity,
            "goal": self.goal,
        }


def _profile_from_json(data: dict[str, Any]) -> Profile:
    plan_data = data["plan"]
    plan = None
    if plan_data is not None:
        plan = Plan(
            bmr=plan_data["bmr"],
            tdee=plan_data["tdee"],
            target_kcal=plan_data["target_kcal"],
            bmi=plan_data["bmi"],
            macros=Macros(**plan_data["macros"]),
        )
    return Profile(
        name=data["name"],
        gender=data["gender"],
        age=data["age"],
        height_cm=data["height_cm"],
        weight_kg=data["weight_kg"],
        activity=data["activity"],
        goal=data["goal"],
        plan=plan,
    )


class ApiClient:
    def __init__(
        self, base_url: str, api_key: str, *, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url.rstrip("/") + "/api/v1",
            headers={"X-API-Key": api_key},
            timeout=10.0,
            transport=transport,
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = await self._http.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise ApiError(f"API unreachable: {exc}") from exc
        if response.status_code >= 400 and response.status_code != 404:
            raise ApiError(f"API {method} {path} failed with {response.status_code}")
        return response

    async def get_profile(self, telegram_id: int) -> Profile | None:
        response = await self._request("GET", f"/users/{telegram_id}/profile")
        if response.status_code == 404:
            return None
        return _profile_from_json(response.json())

    async def upsert_profile(self, telegram_id: int, profile: ProfileInput) -> Profile:
        response = await self._request(
            "PUT", f"/users/{telegram_id}/profile", json=profile.to_json()
        )
        return _profile_from_json(response.json())

    async def get_language(self, telegram_id: int) -> Lang | None:
        response = await self._request("GET", f"/users/{telegram_id}/language")
        if response.status_code == 404:
            return None
        return Lang(response.json()["language"])

    async def set_language(self, telegram_id: int, language: Lang) -> Lang:
        response = await self._request(
            "PUT", f"/users/{telegram_id}/language", json={"language": language.value}
        )
        return Lang(response.json()["language"])

    async def get_stats(self) -> dict[str, Any]:
        response = await self._request("GET", "/admin/stats")
        return dict(response.json())

    async def list_telegram_ids(self) -> list[int]:
        response = await self._request("GET", "/admin/telegram-ids")
        return [int(value) for value in response.json()["telegram_ids"]]

    async def delete_user(self, telegram_id: int) -> bool:
        response = await self._request("DELETE", f"/admin/users/{telegram_id}")
        return response.status_code == 204

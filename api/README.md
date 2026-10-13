# FitTrack API

REST API that owns all FitTrack data: user profiles, daily nutrition targets and user
language settings. The Telegram bot (`bot/`) is the first client; the website will be
the second. Every request must carry the `X-API-Key` header.

**Stack:** Python 3.12 · FastAPI · PostgreSQL 16 · SQLAlchemy 2.0 (async, asyncpg) · Alembic · pytest

## Quick start

```bash
cp .env.example .env
make install
make migrate
make dev            # http://localhost:8000/docs
```

## Endpoints

All endpoints are under `/api/v1` and need `X-API-Key`. `/health` is public.

| Method | Path                                  | Description                                          |
|--------|---------------------------------------|------------------------------------------------------|
| PUT    | `/users/{telegram_id}/profile`        | Create or update a profile; stores today's weight and returns the plan |
| GET    | `/users/{telegram_id}/profile`        | Profile with the latest weight and plan (404 if none) |
| GET    | `/users/{telegram_id}/language`       | Saved language (404 if not set)                      |
| PUT    | `/users/{telegram_id}/language`       | Set language: `uz`, `ru` or `en`                     |
| GET    | `/admin/stats`                        | Total users, profiles and users per language         |
| GET    | `/admin/telegram-ids`                 | Telegram IDs for broadcasts                          |
| DELETE | `/admin/users/{telegram_id}`          | Delete a user and their settings                     |
| GET    | `/health`                             | Liveness with a database check                       |

## Tests

```bash
docker run -d --name fittrack-test-pg -e POSTGRES_USER=fittrack \
  -e POSTGRES_PASSWORD=fittrack -e POSTGRES_DB=fittrack -p 5433:5432 postgres:16-alpine
TEST_DATABASE_URL=postgresql+asyncpg://fittrack:fittrack@localhost:5433/fittrack make test
```

## Layout

```
app/
├── api/v1/         router (API-key guard) and routes
├── services/       profile, settings and admin use cases; commit boundaries
├── repositories/   SQLAlchemy queries
├── models/         ORM models and enums
├── schemas/        request and response models
├── core/           config, API-key check, nutrition formulas
└── db/             declarative base, async engine and session
migrations/         Alembic revisions
tests/              API and formula tests
```

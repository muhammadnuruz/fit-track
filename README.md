# FitTrack

FitTrack helps people who train seriously track nutrition and body composition. Today it is
a Telegram bot that builds a daily calorie and macro plan from a short profile. The project is
split into two services so the same API can later serve a website as well.

| Service | Path   | Stack                                              | Role                                           |
|---------|--------|----------------------------------------------------|------------------------------------------------|
| API     | `api/` | FastAPI · PostgreSQL · SQLAlchemy 2 · Alembic      | Owns all data and rules (profiles, plans, settings) |
| Bot     | `bot/` | aiogram 3 · httpx · Redis (optional)               | Telegram interface; calls the API over HTTP    |

Each service has its own README with endpoints, configuration and tests.

## Quick start (Docker)

```bash
cp .env.example .env     # set BOT_TOKEN and API_KEY (required), ADMINS (optional)
make up                  # db, redis, api (migrates on start), bot
```

The bot runs in polling mode by default. For webhook mode set `BOT_MODE=webhook`,
`WEBHOOK_BASE_URL` (public `https://` URL) and `WEBHOOK_SECRET` (16–256 letters, digits, `_` or `-`)
in `.env`, and put an HTTPS reverse proxy in front of `BOT_HOST_PORT`.

- API: http://localhost:8000 (health: `/health`, endpoints under `/api/v1`, every call needs `X-API-Key`)
- Postgres is published on host port `5433` (`DB_HOST_PORT`) so it does not clash with a local Postgres.

## Tests

```bash
make test                # api and bot test suites
```

The API tests need a Postgres database (`TEST_DATABASE_URL`). CI runs one automatically.

## Layout

```
api/                  FastAPI service
bot/                  Telegram bot service (polling or webhook)
docker-compose.yml    db, redis, api, bot
.github/workflows/    CI for both services
```

## Design decisions

- **Data lives only in the API.** The bot keeps no database, so the website and the bot always
  see the same profiles and plans.
- **Service-to-service auth is a shared API key.** Telegram initData is no longer used because
  the Mini App was removed.
- **Nutrition formulas are pure functions** (`api/app/core/formulas.py`) with their own tests.
- **Migrations run on API start** (`alembic upgrade head`), so the schema always matches the code.

# FitTrack

FitTrack builds a daily calorie and macro plan from a short user profile.
It has two services:

- `api/` — FastAPI service with PostgreSQL. It stores profiles, plans and settings.
- `bot/` — Telegram bot. It calls the API.

## Run with Docker

```bash
cp .env.example .env
```

Edit `.env` and set `BOT_TOKEN` and `API_KEY`. Then:

```bash
make up
```

This starts Postgres, Redis, the API and the bot. The API applies migrations on start.

- API: http://localhost:8000 (health check: `/health`)
- Postgres: port 5433 on the host

Stop everything with `make down`.

## Bot modes

- `BOT_MODE=polling` (default). No public URL needed.
- `BOT_MODE=webhook`. Set `WEBHOOK_BASE_URL` to a public `https://` URL and `WEBHOOK_SECRET`
  to 16–256 characters (letters, digits, `_`, `-`). Put an HTTPS reverse proxy in front of
  `BOT_HOST_PORT`.

## Tests

```bash
make test
```

The API tests need Postgres. See `api/README.md`.

## Project layout

```
api/                   API service
bot/                   Telegram bot
docker-compose.yml     Postgres, Redis, API, bot
.github/workflows/     CI
```

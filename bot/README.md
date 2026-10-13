# FitTrack Bot

Telegram bot for FitTrack. It has no database of its own: every profile, plan and language
setting lives in the FitTrack API (`api/`) and the bot talks to it over HTTP with `X-API-Key`.

**Stack:** Python 3.12 · aiogram 3 (FSM) · httpx · pydantic-settings · Redis (optional FSM storage)

## Features

- `/start`: pick a language (uz / ru / en), then a welcome message. New users get an onboarding button.
- Onboarding: name, gender, age, height, weight, activity level and goal. The bot saves the profile through the API and replies with the daily plan.
- `/plan`: daily calories, macros, BMI and TDEE. Asks for onboarding if there is no profile yet.
- `/cancel`: leave onboarding.
- `/help`: command list.
- Admin panel (`/admin`, IDs from `ADMINS`): statistics, broadcast to every user, delete a user.

## Quick start

```bash
cp .env.example .env     # BOT_TOKEN, API_KEY (must match the API), API_BASE_URL
make install
make dev
```

The API must be running first (see `api/README.md`).

## Configuration

| Variable       | Default                  | Purpose                                              |
|----------------|--------------------------|------------------------------------------------------|
| `BOT_TOKEN`    | —                        | Token from @BotFather                                |
| `API_BASE_URL` | `http://localhost:8000`  | FitTrack API base URL                                |
| `API_KEY`      | —                        | Must equal the API's `API_KEY`                       |
| `ADMINS`       | empty                    | Comma-separated Telegram IDs with admin access       |
| `REDIS_URL`    | empty                    | FSM storage; empty means in-memory (single instance) |
| `LOG_LEVEL`    | `INFO`                   | Logging level                                        |

## Tests

```bash
make test
```

Tests cover the API client (mocked transport), input validation, plan text and i18n catalogs.

## Layout

```
app/
├── handlers/       common (start, help, language), profile (/plan), onboarding (FSM), admin
├── keyboards/      language, onboarding choices, admin menu
├── middlewares/    throttling, private-only, language lookup through the API
├── i18n/           uz / ru / en catalogs
├── api_client.py   typed HTTP client for the FitTrack API
├── plan_text.py    plan message builder
├── validation.py   name / age / number parsing for onboarding
├── bot.py          bot and dispatcher factories
└── main.py         entrypoint (polling)
tests/
```

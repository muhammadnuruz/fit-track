# FitTrack Bot

Telegram bot for FitTrack. The bot has no database. All data is stored in the API
(`api/`), and the bot reads and writes it over HTTP with the `X-API-Key` header.

Stack: aiogram 3, httpx, pydantic-settings. Redis is optional.

## Commands

| Command   | What it does                                              |
|-----------|-----------------------------------------------------------|
| `/start`  | Choose a language, then start onboarding if there is no profile. |
| `/plan`   | Show the daily plan. Starts onboarding if there is no profile.  |
| `/cancel` | Stop onboarding.                                          |
| `/help`   | Show the command list.                                    |
| `/admin`  | Admin panel (admins only, see `ADMINS`).                  |

Onboarding asks for: name, gender, age, height, weight, activity level and goal.
At the end the bot saves the profile in the API and sends the plan.

The admin panel shows statistics, sends a broadcast to all users, and deletes a user.

## Local setup

```bash
cp .env.example .env
make install
make dev
```

The API must be running. Set `API_BASE_URL` and `API_KEY` in `.env` to match it.

## Configuration

| Variable           | Default                 | Notes                                          |
|--------------------|-------------------------|------------------------------------------------|
| `BOT_TOKEN`        | —                       | Required. Token from @BotFather.               |
| `API_KEY`          | —                       | Required. Same value as the API's `API_KEY`.   |
| `API_BASE_URL`     | `http://localhost:8000` | Base URL of the API.                           |
| `ADMINS`           | empty                   | Comma-separated Telegram IDs.                  |
| `REDIS_URL`        | empty                   | Stores FSM state. Empty means in memory.       |
| `LOG_LEVEL`        | `INFO`                  |                                                |
| `BOT_MODE`         | `polling`               | `polling` or `webhook`.                        |
| `WEBHOOK_BASE_URL` | empty                   | Public `https://` URL. Webhook mode only.      |
| `WEBHOOK_SECRET`   | empty                   | 16–256 characters: letters, digits, `_`, `-`. Webhook mode only. |
| `WEBHOOK_PATH`     | `/webhook`              | Path for the webhook.                          |
| `WEB_HOST`         | `0.0.0.0`               | Webhook server host.                           |
| `WEB_PORT`         | `8080`                  | Webhook server port.                           |

The bot refuses to start if the settings are invalid. It prints the reason.

## Tests

```bash
make test
```

## Layout

```
app/
  handlers/     /start, /help, /plan, onboarding, admin
  keyboards/    buttons and menus
  middlewares/  throttling, private chats only, language lookup
  i18n/         uz, ru, en texts
  api_client.py HTTP client for the API
  plan_text.py  plan message
  validation.py input checks for onboarding
  config.py     settings
  bot.py        bot and dispatcher
  main.py       entrypoint (polling or webhook)
tests/
```

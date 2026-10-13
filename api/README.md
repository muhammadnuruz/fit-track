# FitTrack API

REST API for user profiles, nutrition plans and language settings.
All endpoints are under `/api/v1` and require the `X-API-Key` header.
`/health` does not require a key.

Stack: FastAPI, PostgreSQL, SQLAlchemy 2 (async), Alembic.

## Local setup

```bash
cp .env.example .env
make install
make migrate
make dev
```

Open http://localhost:8000/docs for the interactive docs (not in production).

## Endpoints

| Method | Path                            | Description                                  |
|--------|---------------------------------|----------------------------------------------|
| PUT    | `/users/{telegram_id}/profile`  | Create or update a profile. Returns the plan. |
| GET    | `/users/{telegram_id}/profile`  | Get the profile and plan. 404 if not found.  |
| GET    | `/users/{telegram_id}/language` | Get the language. 404 if not set.            |
| PUT    | `/users/{telegram_id}/language` | Set the language: `uz`, `ru` or `en`.       |
| GET    | `/admin/stats`                  | Count of users, profiles and languages.      |
| GET    | `/admin/telegram-ids`           | All Telegram IDs (for broadcasts).           |
| DELETE | `/admin/users/{telegram_id}`    | Delete a user and their settings.            |
| GET    | `/health`                       | Health check, includes a database check.     |

Profile fields: `name`, `gender`, `age`, `height_cm`, `weight_kg`, `activity`, `goal`.

## Tests

Tests run against a real Postgres database set by `TEST_DATABASE_URL`.

```bash
docker compose up -d db
docker compose exec db psql -U fittrack -d fittrack -c "CREATE DATABASE fittrack_test;"
TEST_DATABASE_URL=postgresql+asyncpg://fittrack:fittrack@localhost:5433/fittrack_test make test
```

Run the first two commands once. The `CREATE DATABASE` step fails if the database already exists; that is fine.

## Migrations

```bash
make makemigration m="describe the change"   # generate from model changes
make migrate                                  # apply
```

## Layout

```
app/
  api/v1/       routes and the API-key guard
  services/     use cases; commit happens here
  repositories/ SQL queries
  models/       ORM models and enums
  schemas/      request and response models
  core/         config, API-key check, nutrition formulas
  db/           base class, engine, session
migrations/     Alembic revisions
tests/
```

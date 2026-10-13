# Handoff

Short notes for the next developer. Update this file when the layout or the process changes.

## What exists

- `api/`: profiles, nutrition plan, language settings, admin endpoints. Postgres, Alembic migration `0001_initial`.
- `bot/`: onboarding, `/plan`, language selection, admin panel. Polling or webhook.
- Nutrition formulas in `api/app/core/formulas.py`, covered by tests.

Not built yet: food database and food logging.

## Next step: food logging

1. Food table, migration and endpoints. Source: USDA or Open Food Facts. Add 30–50 local dishes by hand.
2. Log entries from text, for example "plov 300g". Match the dish, calculate macros for the portion, store a snapshot.
3. Matching: start with normalized text and trigram or ILIKE search. Add embeddings later if needed.
4. Show what is left for the day after each entry.

Open questions: which food source to use, and how to match text to dishes.

## Conventions

- No code comments and no docstrings.
- One branch per PR. Commit messages in English, imperative mood (`Add ...`, `Remove ...`).
- Do not add AI attribution (`Co-Authored-By`, "Generated with ...") to commits or PRs.
- Before each commit, run in both projects: `ruff check`, `ruff format --check`, `mypy app`, `pytest`.
- API layers: routes → services → repositories → models. Services own the commit.
- Enum columns use `pg_enum()`, which stores the enum value.

## Known gaps

- The bot cannot edit a profile. Users can only repeat onboarding.
- Bot FSM state is in memory unless `REDIS_URL` is set. Multiple bot instances need Redis.
- The Telegram flow has not been tested end to end with a live token.

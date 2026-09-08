# FitTrack Bot 🏋️

> Sport bilan aktiv shug'ullanuvchilar uchun tana tarkibini o'zgartirishga (bulk / cut / PP) yordam beruvchi Telegram bot. **Farqlovchi ustunlik:** aniq makroslar bilan **mahalliy (O'zbek) taom bazasi**.

Batafsil spetsifikatsiya: `SPEC.md` (Downloads papkasida).

---

## Texnologiyalar

| Qatlam | Texnologiya |
|---|---|
| Bot | Aiogram 3 (FSM) |
| API / biznes logika | FastAPI |
| DB | PostgreSQL + **pgvector** |
| ORM / migratsiya | SQLAlchemy 2.0 (async) + Alembic |
| Scheduler | APScheduler |
| Grafik | matplotlib |
| Embedding | sentence-transformers (ixtiyoriy) |

## Loyiha tuzilishi

```
app/
├── config.py          # pydantic-settings sozlamalari
├── main.py            # kirish nuqtasi (bot + api)
├── logging_config.py  # structlog
├── db/                # engine, session, Base
├── models/            # SQLAlchemy modellari (users, foods, ...)
├── core/              # formulalar (BMR/TDEE/makros/Navy) + tavsiya dvijoki
├── services/          # taom moslash, loglash xizmatlari
├── bot/               # aiogram: handlers, keyboards, FSM states
├── api/               # FastAPI routelari
└── scheduler/         # haftalik check-in eslatmalari
migrations/            # Alembic
scripts/               # seed_foods.py
tests/                 # pytest (formulalar to'liq qamrovda)
```

## Ishga tushirish (lokal)

**Talab:** Python 3.10–3.12, Docker (Postgres uchun).

```bash
# 1. Virtualenv + bog'liqliklar (python3.10)
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 2. Muhit
cp .env.example .env      # BOT_TOKEN ni to'ldiring

# 3. DB (pgvector) ni ko'tarish
make db-up                # yoki: docker compose up -d db

# 4. Migratsiya
make migrate              # alembic upgrade head

# 5. Testlar
make test

# 6. Botni ishga tushirish
make run
```

Barcha buyruqlar: `make help`.

## Rivojlanish bosqichlari (SPEC §8)

- [x] **Bosqich 0 — Poydevor:** skelet, DB + Alembic, modellar, formulalar + testlar, config, Docker
- [ ] **Bosqich 1 — Yadro:** foods seed, kunlik loglash, vektor moslash, "qancha qoldi"
- [ ] **Bosqich 2 — Tracking:** haftalik check-in, Navy BF%, APScheduler, matplotlib grafik
- [ ] **Bosqich 3 — Aql:** tavsiya dvijoki, admin moderatsiya
- [ ] **Bosqich 4 — Kelajak:** LLM tabiiy so'rov, premium

## Eslatma (maxfiylik va xavflar)

- Yog' foizi = **taxmin**, klinik o'lchov emas.
- Progress fotolar ixtiyoriy; faqat Telegram `file_id` saqlanadi.
- Bu tibbiy maslahat emas — faqat kuzatuv/hisob vositasi.

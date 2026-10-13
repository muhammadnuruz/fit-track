# FitTrack — handoff

Yangi sessiya uchun qisqa holat. Har katta o'zgarishdan keyin yangilang.

## 1. Loyiha
FitTrack — sport bilan shug'ullanuvchilar uchun kaloriya va makro reja (cut / maintain / bulk).
Hozir ishlaydigan qism: Telegram bot. Maqsad: keyin veb-sayt ham shu API'ni ishlatadi.

Repo: `muhammadnuruz/fit-track` (master). Ikki servis, bitta repo:

| Servis | Yo'l   | Stack                                   | Vazifa                                    |
|--------|--------|-----------------------------------------|-------------------------------------------|
| API    | `api/` | FastAPI, PostgreSQL, SQLAlchemy 2, Alembic | Barcha ma'lumot va qoidalar (profil, reja, til) |
| Bot    | `bot/` | aiogram 3, httpx, Redis (ixtiyoriy)     | Telegram interfeysi; API'ga HTTP orqali ulanadi |

Bot DB'siz. Mini App va landing olib tashlangan.

## 2. Ishga tushirish
- Docker (tavsiya): `cp .env.example .env` → `BOT_TOKEN`, `API_KEY` ni to'ldiring → `make up`.
  Postgres host'da `5433` portda (mahalliy Postgres bilan to'qnashmaslik uchun).
- Mahalliy: `cd api && make install && make migrate && make dev`, `cd bot && make install && make dev`.
  Har servis o'zining `.env.example` fayli bilan ishlaydi.
- Testlar: `make test` (ildizdan). API testlari `TEST_DATABASE_URL` ni talab qiladi
  (Postgres konteyneri: `docker compose up -d db`, port 5433, `fittrack_test` DB).

## 3. Bot rejimlari
- `BOT_MODE=polling` (default): mahalliy ishlatish uchun.
- `BOT_MODE=webhook`: `WEBHOOK_BASE_URL` (https, ochiq domen), `WEBHOOK_SECRET`
  (16–256 belgi: harf, raqam, `_`, `-`) majburiy. Konfiguratsiya noto'g'ri bo'lsa bot ishga tushmaydi.
  Webhook port: `WEB_PORT` (default 8080, compose'da `BOT_HOST_PORT`). Oldida reverse proxy (HTTPS) bo'lishi kerak.

## 4. Konvensiyalar
- Kodda izoh (`#`) va docstring yo'q — qat'iy qoida.
- Har branch = bitta PR. Commit xabari: inglizcha, imperativ (`Add ...`, `Remove ...`).
- Commit va PR'larda AI attribution (Co-Authored-By, "Generated with ...") yo'q.
- Har commitdan oldin: `ruff check`, `ruff format --check`, `mypy app`, `pytest` (api va bot).
- Qatlamlar (API): `api/v1/routes` → `services` (commit chegarasi) → `repositories` → `models`.
- Enum ustunlar `pg_enum()` orqali (qiymatni saqlaydi).

## 5. Joriy holat
- API: profil upsert/get (reja bilan), til get/set, admin: statistika, Telegram ID'lar, foydalanuvchini o'chirish.
  Migratsiya `0001_initial` (users, measurements, user_settings). `alembic check` toza.
- Bot: `/start`, til tanlash, chat onboarding (ism, jins, yosh, bo'y, vazn, faollik, maqsad) → reja,
  `/plan`, `/cancel`, `/help`, admin panel (statistika, broadcast, o'chirish). uz / ru / en.
- Formulalar: `api/app/core/formulas.py` (BMR Mifflin–St Jeor, TDEE, makro, BMI, Navy BF%) — testlar bilan.

## 6. Keyingi qadam: Bosqich 1 — ovqat loglash
1. Taom bazasi: jadval (`foods`) + migratsiya + API endpointlar. Manba: USDA (tavsiya) yoki Open Food Facts, va 30–50 o'zbek taomi qo'lda.
2. Kunlik loglash: matn ("palov 300g") → taomni moslash → porsiya bo'yicha makro → `food_logs` (snapshot).
3. Taom moslash: avval normalizatsiya + trigram/ILIKE; embedding keyinroq.
4. "Bugun qancha qoldi": protein/kkal/yog' qolgan miqdori, har logdan keyin.

Hal qilinishi kerak: moslash yondashuvi va ochiq baza manbai.

## 7. Ochiq masalalar
- Bot onboarding'dan keyin foydalanuvchi profilini tahrirlash yo'q (faqat qayta onboarding).
- Bot FSM xotirada (bitta instans). Ko'p instans uchun `REDIS_URL` kerak.
- Telegram'da haqiqiy oqim hali sinalmagan (bot tokeni bilan `make dev` / webhook).

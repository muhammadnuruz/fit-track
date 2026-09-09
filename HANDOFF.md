# FitTrack — Handoff (keyingi sessiya uchun)

> Bu hujjatni yangi sessiyaga tashlang. Loyihaning joriy holati, konvensiyalari va keyingi reja shu yerda.

## 0. Ish uslubi (MUHIM)
- Foydalanuvchi til: **o'zbekcha**. Javoblar o'zbekcha, **hisobotlar jadval (table) ko'rinishida**.
- Foydalanuvchi **orkestratsiya**ni xohlaydi: mexanik ishni **fast-worker** agentga, chuqur mulohazani **deep-reasoner** ga ber; natijani **doim o'zing tekshirib** (ruff+pytest+kerak bo'lsa jonli bot), so'ng commit + jadval hisobot.
- Agentlar ba'zan ishonchsiz — natijani har doim o'zing tasdiqla.
- Buzilishga sezgir yoki mayda aniq ishni to'g'ridan-to'g'ri o'zing qil (tezroq/ishonchli).

## 1. Loyiha
FitTrack — Telegram bot. **Kengaygan maqsad:** faqat ovqat emas, **sog'lom hayot + kuchli tana** (workout, taom, tana qurish) — sekin-asta. **Lekin bosqichlar o'zgarmaydi:** avval to'liq eski ozuqa reja (Bosqich 1) tugatiladi, keyin workout. Spetsifikatsiya: `SPEC.md` (Downloads papkasida) yoki `/Users/muhammadnur/Downloads/SPEC.md`.

Bot: **@FitTrackUzBot** (token `.env` da). GitHub: `github.com/muhammadnuruz/FitTrack` (master).

## 2. Stack va ishga tushirish
- Python **3.10** (venv), aiogram 3.31, FastAPI, SQLAlchemy 2.0 async, Alembic, PostgreSQL+pgvector, APScheduler, matplotlib, structlog.
- **Docker-first:** `docker compose up --build` → DB + migratsiya + bot (hammasi). Kod tahriridan keyin `docker compose restart bot` (live mount). To'xtatish: `docker compose down`. Loglar: `docker compose logs -f bot`.
- **Test/lint** (Docker image'da yo'q — lokal venv):
  ```
  python3.10 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
  pytest         # 30 test o'tishi kerak
  ruff check app tests
  ```
- **DB porti 5433** (host'da 5432'da foydalanuvchining Homebrew Postgres'i bor — tegilmaydi). `.env` da `POSTGRES_PORT=5433`.
- Docker Desktop ba'zan uxlab qoladi → `open -a Docker` bilan uyg'otiladi.

## 3. Kod konvensiyalari (QAT'IY)
- **Hech qanday comment (#) va docstring YO'Q** — butun kod ataylab tozalangan. Yangi kodga ham yozma.
- `ruff` toza, `pytest` 30/30 bo'lishi shart (har commitdan oldin).
- Enum ustunlar `app/db/base.py` dagi `pg_enum()` orqali (qiymatni saqlaydi, nomni emas).
- Git commit oxiri: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. Faqat foydalanuvchi so'raganda push.

## 4. Arxitektura (`app/`)
```
config.py          pydantic-settings (BOT_TOKEN, DB, ADMINS, admin_ids)
main.py            entrypoint (polling)
db/                base(pg_enum), session (async)
models/            user, user_settings, measurement, food, food_log(+daily_summary), enums
core/formulas.py   BMR/TDEE/makros/Navy BF% (SPEC §4) — TO'LIQ TEST QILINGAN
services/settings  get/set/has_language
i18n/              catalog t(key,lang,**kw) + languages(uz/ru/en) + translations/{uz,ru,en}.py
bot/
  bot.py           dispatcher; middleware tartibi: throttling→private_only→db→i18n; routerlar: admin, common
  emoji.py         BARCHA premium emoji ID'lari + helperlar (custom_emoji, flag_emoji, welcome_emojis...)
  handlers/common  /start, /help, til tanlash (inline picker), yangi-user xabari
  admin.py         /admin panel (Statistika, Broadcast) — adminlar only
  access.py        is_admin()
  notifications.py notify_admins_new_user()
  keyboards/        language.py, admin.py
  middlewares/      db, i18n, throttling(0.5s), private_only(guruhda ishlamaydi)
  states.py        Onboarding, CheckIn (FSM holatlari), AdminBroadcast
  commands.py      /start,/help menyu (3 tilda)
migrations/         0001_initial (barcha jadval+pgvector), 0002_user_settings
tests/              test_formulas (matematik o'zak), test_i18n
```

## 5. TAYYOR (qilingan)
| Blok | Holat |
|---|---|
| Bosqich 0: skelet, DB+Alembic, modellar, formulalar+test, config, Docker | ✅ |
| i18n 3 til (uz/ru/en), til `/start`da tanlanadi, doimiy "Tilni o'zgartirish" reply-knopka | ✅ |
| Premium (custom) emoji: knopkalarda (icon_custom_emoji_id, Bot API 9.4) + xabarlarda; ID'lar `emoji.py`da | ✅ |
| /start welcome (umumiy ohang), til tanlash, tasdiq — premium emoji bilan | ✅ |
| Admin: `.env ADMINS`, is_admin, /admin panel (Statistika+Broadcast), yangi-user→adminlarga DM | ✅ |
| Middleware: throttling(0.5s/user), private_only(guruh→rad) | ✅ |
| Bot about + description (Telegram'da, umumiy maqsad) | ✅ |
| **FastAPI + webhook rejimi** (`app/api/app.py`, `main.py` webhook+polling ikkalasi uvicorn ostida) | ✅ |
| **Onboarding Mini App** (WebApp: `/webapp` sahifa, `POST /api/onboarding`, initData HMAC tekshiruvi) | ✅ |
| «▶️ Boshlash» reply-knopka (Play premium emoji, faqat profili yo'q userga) → mini-app | ✅ |

## 6. OCHIQ / KUTILAYOTGAN
- `.env` da **`ADMINS=` BO'SH** — admin panel/xabar ishlashi uchun foydalanuvchi o'z Telegram ID'sini yozishi kerak (`ADMINS=123,456`).
- **Deployment (mini-app uchun MUHIM):** serverda `.env` ga to'ldirish kerak — `BOT_MODE=webhook`, `WEBHOOK_URL=https://domen`, `WEBHOOK_SECRET=...`, `WEBAPP_URL=https://domen/webapp`. Reverse-proxy (nginx) domenni `API_PORT` (default 8000) ga yo'naltirsin. `WEBAPP_URL` https bo'lmasa «Boshlash» knopka ko'rsatilmaydi (lokal dev'da normal).
- **Play emoji ID** (`4969785943297884856`) `emoji.py`da — jonli ishga tushganda `bot.get_custom_emoji_stickers([id])` bilan tasdiqlash tavsiya etiladi.
- **Kanal (FitTrack) va guruh (FitTrack Community) tavsiflari** — matn berilgan, foydalanuvchi **qo'lda** Edit→Description ga joylaydi (bot API bermaydi).
- about/description hozir faqat **uz** (default). Kerak bo'lsa ru/en qo'shish mumkin (`set_my_description(language_code=...)`).
- private_only xabari hozir inglizcha ("Sorry, I only work in private chats") — foydalanuvchi ilgari uz so'ragan edi; kerak bo'lsa uz ga qaytar.
- **Onboarding: FSM (`states.py`) endi ishlatilmaydi** — o'rniga Mini App. Kerak bo'lsa keyingi qadamlar (CheckIn) uchun qoldirildi.

## 7. KEYINGI: Bosqich 1 — Yadro qiymat (SPEC §8)
Tartib (onboarding avval, chunki loglash profilga bog'liq):

1. ~~Onboarding~~ ✅ **BAJARILDI** — Mini App orqali (chat-FSM emas). `app/api/webapp/index.html` (3 tilli forma) → `POST /api/onboarding` (`app/api/routes/onboarding.py`) → `app/services/users.py` (`create_from_onboarding`: `User` + birinchi `Measurement` + `build_nutrition_plan` target'lari + Navy BF%) → reja chatga yuboriladi. initData HMAC: `app/api/security.py` (test bilan). Migratsiya kerak bo'lmadi.
2. **Taom bazasi seed** (`scripts/seed_foods.py`): ochiq baza (**tavsiya: USDA**, aniqroq) + 30–50 qo'lda O'zbek taomi (palov, somsa, mastava, non...). `foods` ga yozish.
3. **Kunlik loglash**: matn ("palov 300g") → taom moslash → porsiya bo'yicha makros → `food_logs` (snapshot).
4. **Taom moslash** (eng nozik qism): **tavsiya — avval normalized-text + trigram/ILIKE** (yengil, torch shart emas); embedding/pgvector keyin. deep-reasoner bilan dizayn qil.
5. **"Bugun qancha qoldi"**: `Protein 88/176g · Kkal 1450/2200 · Yog' 40/70g` — har logdan keyin.

**Tasdiqlanadigan 3 qaror:** (a) moslash: text-first (tavsiya) yoki embedding; (b) ochiq baza: USDA (tavsiya) yoki OpenFoodFacts; (c) boshlanish: onboarding avval (tavsiya).

**DoD:** yangi user profil→reja oladi; ≥30 O'zbek taomi; matn bilan loglash; "qancha qoldi" to'g'ri; ruff toza, testlar o'tadi.

## 8. Premium emoji ID'lari (barchasi `app/bot/emoji.py` da, tasdiqlangan)
wave 👋, smile 😊, salad 🥗, muscle 💪, point 👇, globe/change 🌍, bayroqlar uz/ru/en, check ✅ + admin panel uchun bir nechta (STATISTICS/BROADCAST/ERROR/BLOCKED/...). Yangi emoji qo'shishdan oldin `bot.get_custom_emoji_stickers([id])` bilan tekshir.

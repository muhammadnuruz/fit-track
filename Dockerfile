FROM python:3.12-slim

# Tizim bog'liqliklari (matplotlib, asyncpg build uchun)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Bog'liqliklarni alohida qatlamda o'rnatish (kesh uchun).
# Faqat asosiy to'plam — embeddings (torch) Bosqich 1 da qo'shiladi.
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && pip install "."

COPY . .

# Migratsiya + bot ishga tushirish
CMD ["sh", "-c", "alembic upgrade head && python -m app.main"]

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && pip install "."

COPY . .

CMD ["sh", "-c", "alembic upgrade head && python -m app.main"]

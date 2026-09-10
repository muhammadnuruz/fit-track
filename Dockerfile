# ---- Builder stage: compiles/installs the project into a venv ----
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && pip install "."

COPY . .

# ---- Runtime stage: no build tools, no compilers ----
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

# docker-compose mounts ./app, ./migrations, ./alembic.ini (and ./scripts) over
# these paths at runtime, so they may be host-owned; appuser only needs to
# read/execute them (PYTHONDONTWRITEBYTECODE avoids any pyc write attempts).
USER appuser

HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=20s \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else sys.exit(1)"

CMD ["python", "-m", "app.main"]

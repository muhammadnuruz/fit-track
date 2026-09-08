.PHONY: help install install-ml db-up db-down migrate revision run test lint fmt typecheck clean

help:  ## Buyruqlar ro'yxati
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install:  ## Virtualenv yaratib, dev bog'liqliklarni o'rnatish
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]"

install-ml:  ## Embedding (sentence-transformers) qo'shimchasini o'rnatish
	. .venv/bin/activate && pip install -e ".[embeddings]"

db-up:  ## Postgres (pgvector) konteynerini ko'tarish
	docker compose up -d db

db-down:  ## DB konteynerini to'xtatish
	docker compose down

migrate:  ## Migratsiyalarni qo'llash (head gacha)
	. .venv/bin/activate && alembic upgrade head

revision:  ## Yangi migratsiya yaratish:  make revision m="izoh"
	. .venv/bin/activate && alembic revision --autogenerate -m "$(m)"

run:  ## Botni lokal ishga tushirish
	. .venv/bin/activate && python -m app.main

test:  ## Testlarni ishga tushirish
	. .venv/bin/activate && pytest

lint:  ## Ruff bilan tekshirish
	. .venv/bin/activate && ruff check app tests

fmt:  ## Ruff bilan formatlash
	. .venv/bin/activate && ruff format app tests && ruff check --fix app tests

typecheck:  ## Mypy bilan tip tekshirish
	. .venv/bin/activate && mypy app

clean:  ## Kesh fayllarini tozalash
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov

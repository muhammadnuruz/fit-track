.PHONY: help install install-ml db-ensure db-up db-down migrate revision run up up-build logs down test lint fmt typecheck clean

help:  ## Buyruqlar ro'yxati
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install:  ## Virtualenv yaratib, dev bog'liqliklarni o'rnatish
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]"

install-ml:  ## Embedding (sentence-transformers) qo'shimchasini o'rnatish
	. .venv/bin/activate && pip install -e ".[embeddings]"

db-ensure:  ## Docker DB ni ko'tarib, sog'lom bo'lguncha kutish (daemon o'chiq bo'lsa ham)
	@bash scripts/db_ensure.sh

db-up: db-ensure  ## db-ensure ning aliasi

db-down:  ## DB konteynerini to'xtatish
	docker compose down

migrate: db-ensure  ## DB ni ko'tarib, migratsiyalarni qo'llash
	. .venv/bin/activate && alembic upgrade head

revision:  ## Yangi migratsiya yaratish:  make revision m="izoh"
	. .venv/bin/activate && alembic revision --autogenerate -m "$(m)"

# --- HOST rejimi: DB Docker'da, bot host'da (tez iteratsiya uchun tavsiya etiladi) ---
run: db-ensure migrate  ## DB (Docker) + migratsiya + botni host'da ishga tushirish — HAMMASI birga
	. .venv/bin/activate && python -m app.main

# --- TO'LIQ DOCKER rejimi (Docker-first): bot ham, DB ham Docker'da ---
up: db-ensure  ## Bot + DB ni to'liq Docker'da ishga tushirish (fon rejimida)
	docker compose up -d
	@echo "✅ Bot Docker'da ishlayapti. Loglar:  make logs"

up-build:  ## Bot image'ini qayta qurib, to'liq Docker'da ishga tushirish
	docker compose up -d --build
	@echo "✅ Bot qayta qurildi va ishga tushdi. Loglar:  make logs"

logs:  ## Docker'dagi bot loglarini kuzatish
	docker compose logs -f bot

down:  ## Barcha konteynerlarni to'xtatish
	docker compose down

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

.PHONY: install dev lint format typecheck test migrate makemigration

install:
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy app

test:
	pytest

migrate:
	alembic upgrade head

makemigration:
	alembic revision --autogenerate -m "$(m)"

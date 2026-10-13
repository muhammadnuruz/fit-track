.PHONY: install dev lint format typecheck test

install:
	pip install -e ".[dev]"

dev:
	python -m app.main

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy app

test:
	pytest

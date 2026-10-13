.PHONY: up down logs api-test bot-test test

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

api-test:
	$(MAKE) -C api test

bot-test:
	$(MAKE) -C bot test

test: api-test bot-test

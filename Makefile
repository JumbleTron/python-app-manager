.PHONY: docker-build docker-test docker-lint docker-typecheck docker-binary docker-shell docker-up docker-down

docker-build:
	docker compose build tool

docker-test:
	docker compose run --rm tool pytest

docker-lint:
	docker compose run --rm tool ruff check src tests

docker-typecheck:
	docker compose run --rm tool mypy src

docker-binary:
	mkdir -p dist
	docker compose run --rm tool pyinstaller --clean --noconfirm create-python-app.spec

docker-shell:
	docker compose run --rm tool bash

docker-up:
	docker compose up -d mysql

docker-down:
	docker compose down

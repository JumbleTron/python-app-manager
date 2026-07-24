.PHONY: docker-build docker-test docker-lint docker-typecheck docker-binary docker-binary-test integration-build integration-test integration-down docker-shell docker-up docker-down

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

docker-binary-test: docker-binary
	docker compose run --rm tool ./dist/create-python-app --version
	docker compose run --rm tool ./dist/create-python-app --help

integration-build: docker-binary
	docker compose -f compose.yaml -f compose.integration.yaml build integration-vps

integration-test: integration-build
	docker compose -f compose.yaml -f compose.integration.yaml up -d integration-vps
	trap '$(MAKE) integration-down' EXIT; docker compose -f compose.yaml -f compose.integration.yaml exec integration-vps bash /workspace/scripts/integration-test.sh

integration-down:
	docker compose -f compose.yaml -f compose.integration.yaml down --volumes --remove-orphans

docker-shell:
	docker compose run --rm tool bash

docker-up:
	docker compose up -d mysql

docker-down:
	docker compose down

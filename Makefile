.PHONY: backend-sync backend-test backend-lint backend-typecheck web-install web-test web-build api stream-api worker demo-graph dev-infra verify

backend-sync:
	cd apps/backend && uv sync --dev

backend-test:
	cd apps/backend && uv run pytest

backend-lint:
	cd apps/backend && uv run ruff check src tests

backend-typecheck:
	cd apps/backend && uv run mypy src

web-install:
	cd apps/web && pnpm install

web-test:
	cd apps/web && pnpm test --run

web-build:
	cd apps/web && pnpm build

api:
	cd apps/backend && uv run uvicorn enterprise_agent.entrypoints.api.main:app --reload --port 8000

stream-api:
	cd apps/backend && uv run uvicorn enterprise_agent.entrypoints.stream_api.main:app --reload --port 8001

worker:
	cd apps/backend && uv run celery -A enterprise_agent.entrypoints.workers.celery_app:celery_app worker -Q agent.realtime,agent.resume --loglevel=INFO

demo-graph:
	cd apps/backend && uv run python ../../scripts/demo_graph.py

dev-infra:
	docker compose -f deploy/compose/compose.yml -f deploy/compose/compose.dev.yml up --build

verify:
	./scripts/verify.sh

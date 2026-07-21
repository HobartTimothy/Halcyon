# Enterprise LangGraph AI Agent

A modular-monolith foundation for an enterprise AI agent using FastAPI, LangGraph, Celery, Next.js, PostgreSQL/pgvector, Valkey, RabbitMQ, S3-compatible object storage, and LiteLLM.

The current increment is deliberately deterministic. It proves repository boundaries, parallel graph execution, typed contracts, worker routing, API/SSE entrypoints, and deployment topology before real model, RAG, authentication, memory, and external side-effect integrations are added.

## Repository layout

```text
apps/backend     Python modular monolith and process entrypoints
apps/web         Next.js user and administration shell
contracts        Cross-language event contracts
deploy            Dockerfiles, Compose, and Nginx
configs           Provider and gateway configuration
docs              Architecture, ADRs, plans, and roadmap
```

## Local commands

```bash
make backend-sync
make backend-test
make backend-lint
make backend-typecheck
make web-install
make web-test
make web-build
make api
make stream-api
make worker
make demo-graph
make dev-infra
make verify
```

## Demo API

Start the API:

```bash
make api
```

Execute the deterministic parallel graph:

```bash
curl -X POST http://localhost:8000/api/v1/runs/demo \
  -H 'content-type: application/json' \
  -d '{"query":"leave policy"}'
```

## Design and implementation documents

- `docs/architecture/enterprise-langgraph-ai-system-design-v1.0.docx`
- `docs/superpowers/plans/2026-07-21-foundation-runtime-skeleton.md`
- `docs/implementation/roadmap.md`
- `docs/architecture/module-boundaries.md`

## Frontend dependency lock

The web package pins direct dependency versions exactly. The current build environment could not reach the npm registry, so the first successful `make web-install` will generate `apps/web/pnpm-lock.yaml`; review and commit that lock file before using the skeleton as a release baseline.

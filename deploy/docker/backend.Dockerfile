FROM ghcr.io/astral-sh/uv:0.10.0 AS uv
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH=/app/.venv/bin:$PATH

RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY --from=uv /uv /usr/local/bin/uv
COPY apps/law-agent-backend/pyproject.toml apps/law-agent-backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY apps/law-agent-backend/src ./src
RUN uv pip install --no-deps --editable .
USER appuser
CMD ["uvicorn", "enterprise_agent.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
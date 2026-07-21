#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT/apps/backend"
uv sync --dev --locked
uv run ruff check src tests
uv run mypy src
uv run pytest

cd "$ROOT/apps/web"
if [[ ! -d node_modules ]]; then
  pnpm install --no-frozen-lockfile
fi
pnpm typecheck
pnpm test --run
pnpm build

cd "$ROOT"
python - <<'PY'
from pathlib import Path
import yaml
path = Path("deploy/compose/compose.yml")
doc = yaml.safe_load(path.read_text())
assert "services" in doc and "api" in doc["services"]
print("compose contract: ok")
PY

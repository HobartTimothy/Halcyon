# Halcyon 企业级 LangGraph AI 智能体

Halcyon 是一个面向企业场景的 **LangGraph 多智能体模块化单体项目骨架**。项目采用统一代码仓库管理 FastAPI、LangGraph、Celery、Next.js、PostgreSQL/pgvector、Valkey、RabbitMQ、S3 兼容对象存储和 LiteLLM，并通过多个进程入口隔离 API、SSE、智能体任务和前端运行负载。

当前版本为 **V0.1 Foundation Runtime Skeleton**。本阶段优先验证工程边界、并行图执行、强类型契约、Worker 队列路由、API/SSE 入口和 Docker Compose 部署拓扑。真实大模型调用、完整 RAG、JWT/RBAC、长期记忆、人工审批和外部写操作将在后续阶段逐步实现。

---

## 1. 当前版本包含的能力

### 已实现并完成后端验证

- FastAPI 普通 API 与独立 SSE API 进程入口；
- LangGraph 三路并行执行：RAG、联网搜索、长期记忆；
- 并行结果 fan-out / fan-in 汇合；
- 幂等 Evidence Reducer，避免重复证据膨胀；
- 代码注册式 Skill SDK 基础结构；
- Skill 风险等级、审批要求和副作用幂等约束；
- Celery 应用工厂及 `agent.realtime`、`agent.resume` 队列路由；
- Python、JSON Schema 和 TypeScript 三端 Run Event 契约；
- API 健康检查与确定性 Demo Run；
- Docker Compose 服务拓扑契约；
- Ruff、mypy、pytest、GitHub Actions 基础配置。

### 已生成但需要在本地完成构建验证

- Next.js 聊天应用壳；
- TypeScript/Zod API 与事件解析器；
- Vitest 组件测试；
- Web Docker 镜像。

首次成功执行 `pnpm install` 后，需要提交生成的：

```text
apps/web/pnpm-lock.yaml
```

### 后续阶段实现

- PostgreSQL 业务持久化和 Alembic Migration；
- Transactional Outbox；
- JWT Access Token、Refresh Session 和 RBAC；
- LangGraph PostgreSQL Checkpointer；
- 文档加载、解析、分片、Embedding 和 pgvector；
- 关键词、向量、RRF 和 Rerank 混合检索；
- Tavily 与受控网页抓取；
- LiteLLM 真实模型路由；
- LangGraph `interrupt()` 人工审批；
- Skill 沙箱、受控网络和执行补偿；
- 长期记忆提取、版本和用户治理；
- Prompt Registry、Promote 和 Rollback；
- OpenTelemetry、审计、安全加固和生产发布体系。

---

## 2. 技术栈

| 领域 | 技术 |
|---|---|
| 后端语言 | Python 3.13 / 3.14 |
| API | FastAPI |
| 智能体编排 | LangGraph |
| 后台任务 | Celery |
| 前端 | Next.js 16、React 19、TypeScript 6 |
| 前端校验 | Zod |
| 主数据库 | PostgreSQL 18 |
| 向量检索 | pgvector |
| 缓存与事件流 | Valkey |
| 消息代理 | RabbitMQ |
| 对象存储 | S3 兼容接口，开发环境使用 SeaweedFS |
| 模型网关 | LiteLLM |
| 反向代理 | Nginx |
| Python 依赖 | uv |
| 前端依赖 | pnpm |
| 测试 | pytest、Hypothesis、Vitest、Testing Library |
| 代码质量 | Ruff、mypy、ESLint、TypeScript |

---

## 3. 项目目录

```text
Halcyon/
├── apps/
│   ├── backend/                     # Python 模块化单体后端
│   │   ├── src/enterprise_agent/
│   │   │   ├── bootstrap/          # 配置与启动装配
│   │   │   ├── entrypoints/        # API、SSE、Celery 进程入口
│   │   │   ├── modules/            # Agent Runtime、Skill 等业务模块
│   │   │   └── shared/             # 跨模块共享契约
│   │   ├── tests/                  # 单元、Graph、API、契约测试
│   │   ├── pyproject.toml
│   │   └── uv.lock
│   └── web/                         # Next.js 用户端和管理后台骨架
├── configs/                         # LiteLLM 等运行配置
├── contracts/                       # 跨语言 JSON Schema
├── deploy/
│   ├── compose/                     # Docker Compose
│   ├── docker/                      # 后端与前端 Dockerfile
│   └── nginx/                       # Nginx 路由
├── docs/
│   ├── architecture/                # 架构说明与 ADR
│   ├── implementation/              # 实施路线与状态
│   └── superpowers/plans/           # 详细实施计划
├── scripts/                         # 演示和验证脚本
├── .env.example
├── Makefile
└── README.md
```

---

## 4. 开发环境要求

建议安装：

- Git；
- uv；
- Python 3.14，Python 3.13 也受支持；
- Node.js 24 LTS；
- pnpm 11.15.1；
- Docker Desktop 或 Docker Engine；
- Docker Compose v2。

检查命令：

```bash
git --version
uv --version
python --version
node --version
pnpm --version
docker --version
docker compose version
```

Windows PowerShell 推荐通过 uv 安装 Python：

```powershell
winget install --id astral-sh.uv -e
uv python install 3.14
```

启用项目要求的 pnpm：

```powershell
npm install --global corepack@latest
corepack enable pnpm
pnpm --version
```

---

## 5. 将项目放入 Halcyon 目录

项目根目录应直接包含 `apps`、`deploy`、`docs` 和 `README.md`。

正确结构：

```text
D:\Halcyon\apps
D:\Halcyon\deploy
D:\Halcyon\README.md
```

进入项目：

```powershell
Set-Location D:\Halcyon
```

Linux 或 macOS：

```bash
cd ~/Halcyon
```

复制开发配置：

```powershell
Copy-Item .env.example .env
```

Linux 或 macOS：

```bash
cp .env.example .env
```

开发环境示例：

```dotenv
POSTGRES_DB=enterprise
POSTGRES_USER=enterprise
POSTGRES_PASSWORD=halcyon-dev-postgres
RABBITMQ_USER=enterprise
RABBITMQ_PASSWORD=halcyon-dev-rabbitmq
LITELLM_MASTER_KEY=halcyon-dev-litellm
HTTP_PORT=8080
```

`.env` 只用于本地开发，不要提交到 Git，也不要在生产环境继续使用示例密码。

---

## 6. 后端安装与验证

进入后端目录：

```powershell
Set-Location D:\Halcyon\apps\backend
```

安装锁定依赖：

```powershell
uv sync --python 3.14 --dev --locked
```

运行测试：

```powershell
uv run pytest
```

运行代码检查：

```powershell
uv run ruff check src tests
uv run mypy src
```

当前骨架基线应包含 17 个后端测试。新增功能后，测试数量会继续增加，不应把固定数量作为永久判断条件；应以全部测试通过为准。

运行确定性 LangGraph 演示：

```powershell
uv run python ../../scripts/demo_graph.py
```

输出中应包含三类并行证据：

```text
rag
web
memory
```

当前三个节点返回的是确定性演示数据，目的是验证 LangGraph 并行拓扑和 reducer，而不是真实知识库、搜索和长期记忆结果。

---

## 7. 启动后端 API

在 `apps/backend` 目录执行：

```powershell
uv run uvicorn enterprise_agent.entrypoints.api.main:app `
  --reload `
  --host 127.0.0.1 `
  --port 8000
```

Linux 或 macOS：

```bash
uv run uvicorn enterprise_agent.entrypoints.api.main:app \
  --reload \
  --host 127.0.0.1 \
  --port 8000
```

API 文档：

```text
http://localhost:8000/docs
```

健康检查：

```powershell
Invoke-RestMethod http://localhost:8000/health/live
Invoke-RestMethod http://localhost:8000/health/ready
```

预期：

```json
{"status":"ok"}
```

```json
{"status":"ready"}
```

执行 Demo Run：

```powershell
$Body = @{
  query = "公司年假制度是什么？"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:8000/api/v1/runs/demo" `
  -Method Post `
  -ContentType "application/json" `
  -Body $Body
```

使用 curl：

```bash
curl -X POST http://localhost:8000/api/v1/runs/demo \
  -H "Content-Type: application/json" \
  -d '{"query":"公司年假制度是什么？"}'
```

返回结构：

```json
{
  "run_id": "自动生成的 UUID",
  "final_answer": "Collected 3 evidence items for: 公司年假制度是什么？",
  "evidence_count": 3
}
```

---

## 8. 启动 SSE API

新开一个终端，在 `apps/backend` 目录执行：

```powershell
uv run uvicorn enterprise_agent.entrypoints.stream_api.main:app `
  --reload `
  --host 127.0.0.1 `
  --port 8001
```

测试 SSE：

```powershell
curl.exe -N "http://localhost:8001/api/v1/runs/demo-run/events"
```

预期：

```text
id: 0-0
event: stream.snapshot
data: {"schema_version":"1.0","event_id":"0-0",...}
```

当前 SSE 入口只返回基础快照。后续阶段将替换为 Valkey Streams 读取器，并支持：

- Token 增量输出；
- 节点进度事件；
- 引用事件；
- 审批事件；
- `Last-Event-ID` 断线恢复。

---

## 9. 启动 Celery Worker

Worker 需要 RabbitMQ。可以先通过 Docker 启动基础设施，或者直接启动完整 Compose。

在 `apps/backend` 目录执行：

```powershell
uv run celery `
  -A enterprise_agent.entrypoints.workers.celery_app:celery_app `
  worker `
  -Q agent.realtime,agent.resume `
  --loglevel=INFO
```

当前队列：

```text
agent.realtime    新建智能体 Run
agent.resume      审批或中断后的 Run 恢复
```

---

## 10. 前端安装与运行

进入前端目录：

```powershell
Set-Location D:\Halcyon\apps\web
```

安装依赖：

```powershell
pnpm install
```

第一次成功安装后，应生成并提交：

```text
apps/web/pnpm-lock.yaml
```

验证：

```powershell
pnpm lint
pnpm typecheck
pnpm test --run
pnpm build
```

启动开发服务器：

```powershell
pnpm dev
```

访问：

```text
http://localhost:3000
```

当前前端主要用于验证聊天页面和跨端事件契约。完整联调建议通过 Nginx 和 Docker Compose 访问，以保证 `/api/v1` 路由正确转发。

---

## 11. Docker Compose 一键启动

在项目根目录执行：

```powershell
Set-Location D:\Halcyon
```

检查配置：

```powershell
docker compose `
  --env-file .env `
  -f deploy/compose/compose.yml `
  -f deploy/compose/compose.dev.yml `
  config
```

启动：

```powershell
docker compose `
  --env-file .env `
  -f deploy/compose/compose.yml `
  -f deploy/compose/compose.dev.yml `
  up --build
```

Linux 或 macOS：

```bash
docker compose \
  --env-file .env \
  -f deploy/compose/compose.yml \
  -f deploy/compose/compose.dev.yml \
  up --build
```

服务包括：

| 服务 | 作用 |
|---|---|
| `postgres` | PostgreSQL 18 + pgvector |
| `valkey` | 缓存、结果后端和后续 SSE Streams |
| `rabbitmq` | Celery Broker |
| `seaweedfs` | 开发环境 S3 兼容对象存储 |
| `litellm` | 统一模型网关，目前未配置真实模型 |
| `api` | FastAPI 普通 API |
| `stream-api` | FastAPI SSE API |
| `agent-worker` | LangGraph/Celery Agent Worker |
| `web` | Next.js 前端 |
| `nginx` | 统一入口和反向代理 |

统一访问入口：

```text
http://localhost:8080
```

通过 Nginx 调用 Demo Run：

```powershell
$Body = @{ query = "测试企业智能体" } | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:8080/api/v1/runs/demo" `
  -Method Post `
  -ContentType "application/json" `
  -Body $Body
```

测试 SSE：

```powershell
curl.exe -N "http://localhost:8080/api/v1/runs/demo-run/events"
```

停止并保留数据：

```powershell
docker compose `
  --env-file .env `
  -f deploy/compose/compose.yml `
  -f deploy/compose/compose.dev.yml `
  down
```

停止并删除本地数据卷：

```powershell
docker compose `
  --env-file .env `
  -f deploy/compose/compose.yml `
  -f deploy/compose/compose.dev.yml `
  down -v
```

`down -v` 会删除 PostgreSQL、Valkey、RabbitMQ 和对象存储中的本地数据，请谨慎使用。

---

## 12. Makefile 快捷命令

Linux、macOS、WSL 或安装了 GNU Make 的 Windows 环境可以使用：

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

Windows 原生 PowerShell 默认没有 `make`，可以直接使用前面列出的 `uv`、`pnpm` 和 `docker compose` 命令。

---

## 13. 推荐开发顺序

当前骨架完成后，建议严格按以下顺序推进：

```text
1. PostgreSQL 异步基础设施
2. Alembic Migration
3. Transactional Outbox
4. 用户、Session、JWT 和 RBAC
5. LangGraph PostgreSQL Checkpointer
6. 文档上传和对象存储
7. 文档解析、分片和 Embedding
8. pgvector 与混合检索
9. 联网搜索和安全抓取
10. LiteLLM 真实模型路由
11. Skill、审批和沙箱
12. 长期记忆
13. Prompt Registry 和 Promote
14. OpenTelemetry、审计和生产加固
```

不要在持久化、身份和权限尚未完成前，直接实现外部写 Skill 或生产级长期记忆。

---

## 14. 测试驱动开发流程

每个功能采用：

```text
RED：先写失败测试
GREEN：实现最小可用代码
REFACTOR：保持测试通过后重构
```

后端常用命令：

```powershell
Set-Location D:\Halcyon\apps\backend

uv run pytest tests\path\to\test_file.py -v
uv run ruff check src tests
uv run mypy src
uv run pytest
```

前端常用命令：

```powershell
Set-Location D:\Halcyon\apps\web

pnpm lint
pnpm typecheck
pnpm test --run
pnpm build
```

提交前检查：

```powershell
Set-Location D:\Halcyon
git status
git diff
```

建议每个独立、可验证的任务单独提交：

```powershell
git add .
git commit -m "feat: add asynchronous database engine"
```

---

## 15. 配置说明

后端使用 `EA_` 前缀读取运行配置，例如：

```dotenv
EA_ENVIRONMENT=development
EA_DATABASE_URL=postgresql+psycopg://enterprise:password@localhost:5432/enterprise
EA_BROKER_URL=amqp://enterprise:password@localhost:5672//
EA_RESULT_BACKEND_URL=redis://localhost:6379/1
EA_REALTIME_STREAM_URL=redis://localhost:6379/0
EA_MODEL_GATEWAY_URL=http://localhost:4000
```

当前 `configs/litellm.yaml` 中：

```yaml
model_list: []
```

表示尚未配置真实模型。接入模型时，应通过环境变量或 Secret 注入供应商密钥，不要将 API Key 写入 Git。

---

## 16. 常见问题

### `uv sync --locked` 失败

确认使用项目自带的 `uv.lock`，并检查 Python 版本：

```powershell
uv python list
uv sync --python 3.14 --dev --locked
```

### `pnpm install` 无法连接 Registry

检查网络、代理和 Registry：

```powershell
pnpm config get registry
pnpm config set registry https://registry.npmjs.org/
pnpm install
```

企业网络使用内部 npm 镜像时，应按企业要求配置，不要绕过安全策略。

### `docker info` 无法连接

启动 Docker Desktop，并确认：

```powershell
docker info
docker compose version
```

### 端口被占用

默认端口：

```text
3000   Next.js 本地开发
8000   FastAPI API
8001   SSE API
8080   Nginx Compose 入口
```

可以在 `.env` 修改：

```dotenv
HTTP_PORT=8088
```

### Compose 启动后 LiteLLM 没有可用模型

这是当前 V0.1 的预期状态。Demo Graph 不依赖真实模型。真实模型路由将在后续 Model Gateway 阶段实现。

### API 返回的 RAG、Web、Memory 结果不是真实数据

这是当前 Foundation Skeleton 的预期行为。三个分支是确定性演示节点，只用于证明并行执行、状态合并和 API 契约。

---

## 17. 安全注意事项

- 不要提交 `.env`、API Key、密码和 Token；
- 不要将生产数据库和消息队列端口暴露到公网；
- 不要在 Skill 中使用 `eval()`、`exec()` 或任意 Shell；
- 不要把网页、文档或用户输入当作系统指令执行；
- 外部写操作必须具备审批、幂等键和执行凭证；
- 权限检查必须在后端执行，不能依赖前端隐藏按钮；
- 用户问题、文档和模型内容进入日志前必须脱敏；
- 生产部署必须替换全部示例密码并使用 Secret 管理。

---

## 18. 设计与实施文档

- `docs/architecture/enterprise-langgraph-ai-system-design-v1.0.docx`  
  完整系统设计说明书。

- `docs/architecture/module-boundaries.md`  
  模块边界和依赖规则。

- `docs/architecture/adr/0001-modular-monolith.md`  
  模块化单体决策。

- `docs/architecture/adr/0002-one-thread-per-run.md`  
  每个 Run 独立 LangGraph Thread 的决策。

- `docs/architecture/adr/0003-valkey-and-s3-ports.md`  
  Valkey 与 S3 抽象端口决策。

- `docs/implementation/foundation-status.md`  
  当前骨架的验证状态和延期范围。

- `docs/implementation/roadmap.md`  
  完整实施路线图。

- `docs/superpowers/plans/2026-07-21-foundation-runtime-skeleton.md`  
  Foundation Runtime Skeleton 详细实施计划。

---

## 19. 当前里程碑

```text
版本：V0.1
阶段：Foundation Runtime Skeleton
状态：后端骨架与契约已完成；前端需要在可访问 npm Registry 的环境中完成首次锁定和构建验证
下一阶段：PostgreSQL 持久化、Transactional Outbox、JWT Refresh Session 与 RBAC
```

Halcyon 的目标不是快速堆叠一个无法治理的“万能 Agent”，而是逐步建设一个可测试、可审计、可恢复、可扩展的企业级智能体平台。
* **LangChain**：模型、Prompt、Document、Retriever、Tool 等基础组件。
* **LangGraph**：多 Agent 编排、共享状态、条件路由、循环审核、断点恢复、多轮会话。
* **LangSmith**：调用链追踪、Prompt/模型对比、RAG 质量评估、线上监控。
* **FastAPI**：对外提供聊天、文档上传、知识库管理、人工审批接口。
* **PostgreSQL + pgvector**：业务数据、会话数据、向量数据统一存储。
* **Redis**：缓存、限流、异步任务状态。
* **独立 Worker**：文档解析、切分、Embedding、批量评估等耗时任务。

LangGraph 官方将工作流与 Agent 区分为“固定执行路径”和“动态决定工具及流程”，并原生提供持久化、流式输出和中断恢复能力，比较适合你描述的规划、执行、审核、总结协作流程。([Docs by LangChain][1])

---

# 一、推荐架构

```text
                             ┌──────────────────────┐
                             │ Web / App / 企业微信  │
                             └──────────┬───────────┘
                                        │
                                 HTTP / WebSocket
                                        │
                             ┌──────────▼───────────┐
                             │      FastAPI API      │
                             │ 认证、限流、会话、流式 │
                             └──────────┬───────────┘
                                        │
                             ┌──────────▼───────────┐
                             │ LangGraph Supervisor  │
                             │ 路由、规划、状态与流程 │
                             └────┬─────┬─────┬─────┘
                                  │     │     │
                   ┌──────────────┘     │     └──────────────┐
                   ▼                    ▼                    ▼
             Planner Agent       Executor Agent        Reviewer Agent
             任务拆解规划         工具选择与执行          结果审核评分
                   │                    │                    │
                   │          ┌─────────┴─────────┐          │
                   │          ▼                   ▼          │
                   │      RAG Agent           Tool Agent     │
                   │      文档检索问答       DB/API/Search   │
                   │          │                   │          │
                   └──────────┴─────────┬─────────┴──────────┘
                                        ▼
                                Summarizer Agent
                              汇总答案、引用与建议
                                        │
                   ┌────────────────────┼────────────────────┐
                   ▼                    ▼                    ▼
            PostgreSQL/pgvector      Redis             LangSmith
            会话、向量、业务数据      缓存、队列       Trace、评估、监控
```

## 推荐模式：受控的 Hybrid Agent

不要让一个“大 Agent”任意调用所有工具。

采用：

1. Supervisor 判断任务类型。
2. Planner 生成结构化执行计划。
3. Executor 按步骤调用专用 Agent 或工具。
4. Reviewer 检查完整性、事实依据、工具错误和引用。
5. 不合格时有限次数返工。
6. Summarizer 生成最终答案。

这相当于 **Agentic RAG + 固定质量控制节点**。官方文档将 Hybrid RAG 描述为加入查询改写、检索验证和答案验证等环节，在灵活度与可控性之间进行平衡，与你的需求最匹配。([Docs by LangChain][2])

---

# 二、生产级项目目录

```text
enterprise-agent/
├── README.md
├── pyproject.toml
├── uv.lock
├── langgraph.json
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── .env.example
├── .gitignore
│
├── src/
│   └── enterprise_agent/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── dependencies.py
│       │   ├── exception_handlers.py
│       │   ├── middleware.py
│       │   ├── schemas/
│       │   │   ├── chat.py
│       │   │   ├── document.py
│       │   │   ├── knowledge_base.py
│       │   │   └── approval.py
│       │   └── routes/
│       │       ├── chat.py
│       │       ├── documents.py
│       │       ├── knowledge_bases.py
│       │       ├── conversations.py
│       │       ├── approvals.py
│       │       └── health.py
│       │
│       ├── graph/
│       │   ├── __init__.py
│       │   ├── builder.py
│       │   ├── state.py
│       │   ├── context.py
│       │   ├── routing.py
│       │   ├── commands.py
│       │   ├── events.py
│       │   └── nodes/
│       │       ├── supervisor.py
│       │       ├── planner.py
│       │       ├── executor.py
│       │       ├── reviewer.py
│       │       ├── summarizer.py
│       │       ├── human_approval.py
│       │       ├── error_handler.py
│       │       └── finalize.py
│       │
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── registry.py
│       │   ├── supervisor_agent.py
│       │   ├── planner_agent.py
│       │   ├── rag_agent.py
│       │   ├── database_agent.py
│       │   ├── http_agent.py
│       │   ├── search_agent.py
│       │   ├── python_agent.py
│       │   ├── reviewer_agent.py
│       │   └── summarizer_agent.py
│       │
│       ├── rag/
│       │   ├── __init__.py
│       │   ├── ingestion/
│       │   │   ├── pipeline.py
│       │   │   ├── loaders.py
│       │   │   ├── parser.py
│       │   │   ├── cleaner.py
│       │   │   ├── splitter.py
│       │   │   ├── metadata.py
│       │   │   └── deduplicator.py
│       │   ├── indexing/
│       │   │   ├── indexer.py
│       │   │   ├── embeddings.py
│       │   │   └── vector_store.py
│       │   ├── retrieval/
│       │   │   ├── retriever.py
│       │   │   ├── query_rewriter.py
│       │   │   ├── hybrid_search.py
│       │   │   ├── reranker.py
│       │   │   ├── filters.py
│       │   │   └── compressor.py
│       │   ├── generation/
│       │   │   ├── answer_generator.py
│       │   │   ├── citation_builder.py
│       │   │   └── context_builder.py
│       │   └── evaluation/
│       │       ├── relevance.py
│       │       ├── groundedness.py
│       │       └── answer_quality.py
│       │
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── registry.py
│       │   ├── policies.py
│       │   ├── result.py
│       │   ├── database/
│       │   │   ├── read_sql.py
│       │   │   ├── schema_inspector.py
│       │   │   └── query_validator.py
│       │   ├── http/
│       │   │   ├── client.py
│       │   │   ├── api_tool.py
│       │   │   └── allowlist.py
│       │   ├── search/
│       │   │   ├── web_search.py
│       │   │   └── internal_search.py
│       │   ├── python/
│       │   │   ├── executor.py
│       │   │   ├── sandbox.py
│       │   │   └── serializers.py
│       │   └── documents/
│       │       └── knowledge_search.py
│       │
│       ├── memory/
│       │   ├── __init__.py
│       │   ├── conversation.py
│       │   ├── short_term.py
│       │   ├── long_term.py
│       │   ├── summarization.py
│       │   └── profile_store.py
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── factory.py
│       │   ├── models.py
│       │   ├── fallback.py
│       │   ├── structured.py
│       │   ├── token_counter.py
│       │   └── rate_limiter.py
│       │
│       ├── prompts/
│       │   ├── supervisor.py
│       │   ├── planner.py
│       │   ├── rag.py
│       │   ├── database.py
│       │   ├── reviewer.py
│       │   └── summarizer.py
│       │
│       ├── domain/
│       │   ├── entities/
│       │   │   ├── conversation.py
│       │   │   ├── document.py
│       │   │   ├── knowledge_base.py
│       │   │   └── execution.py
│       │   ├── enums.py
│       │   └── exceptions.py
│       │
│       ├── repositories/
│       │   ├── conversation_repository.py
│       │   ├── document_repository.py
│       │   ├── knowledge_base_repository.py
│       │   ├── execution_repository.py
│       │   └── feedback_repository.py
│       │
│       ├── infrastructure/
│       │   ├── database/
│       │   │   ├── session.py
│       │   │   ├── models.py
│       │   │   └── migrations/
│       │   ├── vectorstore/
│       │   │   └── pgvector_store.py
│       │   ├── cache/
│       │   │   └── redis.py
│       │   ├── checkpoint/
│       │   │   └── postgres.py
│       │   ├── queue/
│       │   │   └── task_queue.py
│       │   └── observability/
│       │       ├── langsmith.py
│       │       ├── logging.py
│       │       └── metrics.py
│       │
│       ├── services/
│       │   ├── chat_service.py
│       │   ├── ingestion_service.py
│       │   ├── knowledge_base_service.py
│       │   ├── approval_service.py
│       │   └── evaluation_service.py
│       │
│       ├── workers/
│       │   ├── document_tasks.py
│       │   ├── embedding_tasks.py
│       │   └── evaluation_tasks.py
│       │
│       ├── config/
│       │   ├── settings.py
│       │   ├── logging.py
│       │   └── constants.py
│       │
│       └── utils/
│           ├── ids.py
│           ├── retry.py
│           ├── serialization.py
│           └── timing.py
│
├── tests/
│   ├── unit/
│   │   ├── graph/
│   │   ├── agents/
│   │   ├── rag/
│   │   └── tools/
│   ├── integration/
│   │   ├── test_rag_pipeline.py
│   │   ├── test_graph_execution.py
│   │   └── test_database_tools.py
│   ├── e2e/
│   │   └── test_chat_api.py
│   ├── evaluations/
│   │   ├── datasets/
│   │   ├── test_groundedness.py
│   │   ├── test_retrieval_quality.py
│   │   └── test_agent_trajectory.py
│   └── fixtures/
│
├── scripts/
│   ├── init_database.py
│   ├── ingest_documents.py
│   ├── rebuild_index.py
│   ├── run_evaluation.py
│   └── export_langsmith_dataset.py
│
├── alembic/
│   ├── env.py
│   └── versions/
│
└── docs/
    ├── architecture.md
    ├── graph-flow.md
    ├── rag-design.md
    ├── tool-security.md
    └── deployment.md
```

LangGraph 官方的最小生产结构通常包括状态、节点、工具、图构建文件、依赖文件、环境变量以及 `langgraph.json`；上面的结构是在该基础上按领域、基础设施和测试进一步拆分。([Docs by LangChain][3])

---

# 三、各 Agent 的职责

## 1. Supervisor Agent

负责识别用户意图和选择流程，不负责真正执行复杂任务。

输出结构建议：

```python
class RouteDecision(BaseModel):
    task_type: Literal[
        "direct_answer",
        "rag",
        "database",
        "http_api",
        "web_search",
        "python_analysis",
        "multi_step",
    ]
    needs_planning: bool
    needs_review: bool
    risk_level: Literal["low", "medium", "high"]
    reason: str
```

典型路由：

```text
简单闲聊             → direct_answer
文档知识问答         → rag_agent
结构化业务查询       → database_agent
外部系统数据查询     → http_agent
最新公开信息         → search_agent
数据计算/文件分析    → python_agent
复合任务             → planner → executor
高风险写操作         → human_approval
```

## 2. Planner Agent

将复杂任务拆解为可执行步骤。

```json
{
  "goal": "分析销售下降原因并给出建议",
  "steps": [
    {
      "id": "step_1",
      "agent": "database_agent",
      "action": "查询最近六个月销售数据",
      "depends_on": []
    },
    {
      "id": "step_2",
      "agent": "rag_agent",
      "action": "检索同期市场活动资料",
      "depends_on": []
    },
    {
      "id": "step_3",
      "agent": "python_agent",
      "action": "计算趋势和同比变化",
      "depends_on": ["step_1"]
    }
  ]
}
```

必须使用 Pydantic 结构化输出，不要让后续节点解析自然语言计划。

## 3. Executor Agent

Executor 本身尽量不直接处理业务，而是：

* 读取当前步骤。
* 查找对应 Agent。
* 调用 Agent。
* 保存执行结果。
* 更新步骤状态。
* 决定继续、重试或终止。

## 4. RAG Agent

负责：

```text
问题理解
  ↓
结合历史消息重写独立问题
  ↓
元数据过滤
  ↓
向量检索 + 关键词检索
  ↓
合并和去重
  ↓
Rerank
  ↓
上下文压缩
  ↓
生成带引用答案
```

LangChain 官方将 RAG 构建块拆分为 Loader、Splitter、Embedding、Vector Store 和 Retriever，且这些组件应保持可替换，避免将具体向量库耦合到 Agent 中。([Docs by LangChain][2])

## 5. Database Agent

建议只让 LLM负责：

* 理解查询意图。
* 选择允许查询的数据域。
* 生成受约束的查询参数或只读 SQL。
* 解释查询结果。

不要直接让它获得数据库管理员连接。

数据库工具层负责：

* SQL AST 解析。
* 禁止 `INSERT/UPDATE/DELETE/DROP/ALTER`。
* 添加最大行数。
* 查询超时。
* 表和字段白名单。
* 敏感字段脱敏。
* 审计日志。

## 6. HTTP Agent

不要提供通用的任意 URL 请求工具，而是将每个外部系统封装成明确工具：

```text
get_customer_info(customer_id)
get_order_status(order_id)
search_product(keyword)
create_service_ticket(...)
```

同时限制：

* 域名白名单。
* 请求超时。
* 重试次数。
* 最大响应体。
* 请求参数校验。
* 认证信息由服务端注入。
* 写操作需要人工审批或幂等键。

## 7. Search Agent

负责搜索公开信息并返回统一结构：

```python
class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str
    published_at: datetime | None
```

搜索结果不应直接作为事实答案，仍需经过：

1. 来源筛选。
2. 页面抓取。
3. 内容抽取。
4. 多来源交叉验证。
5. 引用生成。

## 8. Python Agent

建议运行于隔离容器或沙箱，不要在 API 主进程直接执行模型生成的 Python。

限制：

* CPU 时间。
* 内存。
* 文件目录。
* 网络访问。
* 可导入模块。
* 输出大小。
* 进程数量。
* 执行超时。

## 9. Reviewer Agent

Reviewer 应输出机器可解析结果：

```python
class ReviewResult(BaseModel):
    passed: bool
    score: float
    issues: list[str]
    missing_information: list[str]
    retry_target: str | None
    revised_instruction: str | None
```

审核维度：

* 是否回答用户问题。
* 是否使用了必要工具。
* 是否存在工具异常。
* 文档引用是否真正支持结论。
* SQL/API 数据是否被错误解释。
* 是否遗漏计划步骤。
* 是否包含未经证实的事实。
* 是否泄露内部 Prompt、Token 或敏感数据。

## 10. Summarizer Agent

只读取已经审核通过的材料，负责：

* 合并多个 Agent 结果。
* 删除重复内容。
* 区分事实、推断和建议。
* 生成引用。
* 输出适合用户阅读的最终答案。
* 必要时生成后续建议。

---

# 四、LangGraph 状态设计

`graph/state.py`：

```python
from typing import Annotated, Any, Literal
from typing_extensions import TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class PlanStep(TypedDict):
    id: str
    agent: str
    action: str
    status: Literal["pending", "running", "completed", "failed"]
    retries: int
    result_key: str | None


class AgentState(TypedDict, total=False):
    # 会话
    messages: Annotated[list[AnyMessage], add_messages]
    user_id: str
    thread_id: str
    conversation_id: str

    # 用户请求
    original_query: str
    standalone_query: str
    task_type: str

    # 规划执行
    goal: str
    plan: list[PlanStep]
    current_step_index: int
    artifacts: dict[str, Any]
    tool_results: list[dict[str, Any]]

    # RAG
    knowledge_base_ids: list[str]
    retrieved_documents: list[dict[str, Any]]
    citations: list[dict[str, Any]]

    # 审核
    draft_answer: str
    review_score: float
    review_issues: list[str]
    retry_count: int
    max_retries: int

    # 控制
    next_node: str
    requires_human_approval: bool
    error: str | None

    # 输出
    final_answer: str
```

## 状态设计原则

不要把所有中间内容都塞进 `messages`。

分别保存：

* `messages`：用户和 Agent 对话消息。
* `plan`：结构化执行计划。
* `artifacts`：SQL 结果、API 返回、计算结果等。
* `retrieved_documents`：检索文档及分数。
* `citations`：引用信息。
* `review_issues`：审核问题。
* `final_answer`：最终结果。

这样便于：

* 节点测试。
* 断点恢复。
* LangSmith Trace 分析。
* 前端展示每个执行步骤。
* 控制上下文长度。

---

# 五、推荐 Graph 流程

```text
START
  │
  ▼
load_context
  │
  ▼
supervisor
  │
  ├── direct_answer ───────────────────────┐
  │                                        │
  ├── simple_rag ──► rag_agent ────────────┤
  │                                        │
  └── complex_task                         │
          │                                │
          ▼                                │
       planner                             │
          │                                │
          ▼                                │
       executor ◄──────────────────┐        │
          │                        │        │
          ├── rag_agent            │        │
          ├── database_agent       │        │
          ├── http_agent           │        │
          ├── search_agent         │        │
          └── python_agent         │        │
          │                        │        │
          ▼                        │        │
     step_complete? ── no ─────────┘        │
          │ yes                             │
          ▼                                 │
       reviewer                             │
          │                                 │
          ├── passed ───────────────────────┤
          │                                 │
          ├── retryable ──► executor        │
          │                                 │
          └── approval ──► human_approval   │
                                             │
                                             ▼
                                         summarizer
                                             │
                                             ▼
                                           END
```

建议限制：

```text
最大规划步骤：8
单步骤最大重试：2
审核返工次数：2
单次工具调用超时：15～60 秒
单次 Graph 最大运行时间：按业务配置
```

避免出现无限的：

```text
planner → executor → reviewer → planner
```

---

# 六、多轮问答与记忆

LangGraph 官方区分两类持久化：

* **Checkpointer**：保存单个会话线程的 Graph 状态，用于多轮上下文、恢复、中断和容错。
* **Store**：保存跨线程的长期信息，如用户偏好、事实和共享知识。([Docs by LangChain][4])

建议对应如下：

## 短期记忆

使用 PostgreSQL Checkpointer：

```text
thread_id
├── messages
├── 当前计划
├── 执行步骤
├── 工具结果
└── 中断状态
```

## 长期记忆

单独建立用户记忆表或 LangGraph Store：

```text
user_id
├── 用户偏好
├── 常用知识库
├── 已确认事实
├── 权限范围
└── 对话摘要
```

## 长对话压缩

当消息达到阈值：

```text
旧消息
  ↓
summary node
  ↓
生成结构化历史摘要
  ↓
保留最近 N 轮原始消息
```

摘要建议区分：

```json
{
  "user_goal": "",
  "confirmed_facts": [],
  "decisions": [],
  "unresolved_questions": [],
  "tool_findings": []
}
```

---

# 七、文档入库流程

```text
上传文档
   │
   ▼
文件类型和安全检查
   │
   ▼
解析 PDF / DOCX / HTML / Markdown / Excel
   │
   ▼
文本清洗与结构识别
   │
   ▼
按标题、段落、表格进行语义切分
   │
   ▼
补充元数据
   │
   ▼
内容去重
   │
   ▼
Embedding
   │
   ▼
写入向量库
   │
   ▼
写入文档与分块关系表
```

每个 Chunk 至少保存：

```python
{
    "chunk_id": "...",
    "document_id": "...",
    "knowledge_base_id": "...",
    "content": "...",
    "page_number": 12,
    "section_path": ["第三章", "3.2 权限管理"],
    "source_name": "系统设计说明书.pdf",
    "content_hash": "...",
    "version": 3,
    "access_scope": ["department:technology"],
}
```

关键点：

* 文档内容和向量记录必须有稳定 `chunk_id`。
* 文档更新时按 hash 增量索引。
* 删除文档时同步删除对应向量。
* 权限过滤必须发生在检索阶段，而不是生成答案后。
* 表格最好单独转换为 Markdown 或结构化记录。
* 图片型 PDF 应单独进入 OCR/视觉解析流程。

---

# 八、RAG 检索策略

建议初版采用：

```text
Query Rewrite
    ↓
Metadata Filter
    ↓
Vector Search Top 20
    +
BM25/全文搜索 Top 20
    ↓
Reciprocal Rank Fusion
    ↓
Reranker Top 6
    ↓
Context Compression
    ↓
Answer Generation
```

## 不建议只做向量检索

以下内容关键词检索通常更重要：

* 产品编号。
* 合同编号。
* 人名。
* 错误码。
* API 名称。
* 精确条款。
* 日期、金额、版本号。

因此使用混合检索，并将检索实现封装在 `Retriever` 接口之后。

---

# 九、工具注册机制

`tools/registry.py`：

```python
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    handler: Callable
    risk_level: str
    requires_approval: bool
    timeout_seconds: int
    allowed_agents: tuple[str, ...]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        if definition.name in self._tools:
            raise ValueError(f"Tool already registered: {definition.name}")
        self._tools[definition.name] = definition

    def get_for_agent(self, agent_name: str) -> list[ToolDefinition]:
        return [
            tool
            for tool in self._tools.values()
            if agent_name in tool.allowed_agents
        ]
```

不要把全部工具统一绑定给全部 Agent。

例如：

```text
rag_agent
└── knowledge_search

database_agent
├── inspect_schema
└── execute_readonly_query

http_agent
├── get_customer
└── get_order

python_agent
└── execute_sandboxed_python
```

---

# 十、人工审批

以下操作建议进入 `human_approval`：

* 数据库写操作。
* 外部 API 创建、修改或删除操作。
* 发送邮件、消息。
* 生成并执行代码。
* 大批量数据导出。
* 高成本模型或长时间任务。
* 涉及敏感数据的查询。

LangGraph 的 Interrupt 可以在节点内部暂停执行，将当前状态保存到持久化层，并通过相同 `thread_id` 恢复，适合实现“审核后继续执行”。([Docs by LangChain][5])

---

# 十一、LangSmith 接入位置

建议每次运行包含以下标签：

```python
metadata = {
    "user_id": user_id,
    "conversation_id": conversation_id,
    "thread_id": thread_id,
    "knowledge_base_ids": knowledge_base_ids,
    "task_type": task_type,
    "environment": settings.environment,
}
```

重点追踪：

```text
graph_run
├── supervisor
├── planner
├── executor
│   ├── database_tool
│   ├── retriever
│   ├── reranker
│   └── python_tool
├── reviewer
└── summarizer
```

评估指标：

* Retrieval Recall。
* Context Relevance。
* Answer Groundedness。
* Citation Correctness。
* Task Completion。
* Tool Selection Accuracy。
* Agent Trajectory。
* 延迟。
* Token 消耗。
* 单次请求成本。
* 失败率和重试率。

LangSmith 当前定位不仅是单次 Trace 查看，还包括生产指标、告警、在线评估、反馈采集及自动化工作流，因此应作为独立的可观测性层，而不是只在开发阶段调试 Prompt。([Docs by LangChain][6])

---

# 十二、配置文件建议

```text
.env
├── APP_ENV
├── DATABASE_URL
├── REDIS_URL
├── LLM_PROVIDER
├── LLM_MODEL
├── EMBEDDING_MODEL
├── LANGSMITH_API_KEY
├── LANGSMITH_PROJECT
├── LANGSMITH_TRACING
├── SEARCH_API_KEY
├── TOOL_MAX_RETRIES
├── GRAPH_MAX_RETRIES
└── PYTHON_SANDBOX_URL
```

`langgraph.json`：

```json
{
  "dependencies": ["."],
  "graphs": {
    "enterprise_agent": "./src/enterprise_agent/graph/builder.py:graph"
  },
  "env": ".env"
}
```

---

# 十三、建议实施顺序

## 第一阶段：最小闭环

```text
FastAPI
+ 单知识库
+ 文档上传
+ PostgreSQL/pgvector
+ RAG Agent
+ 多轮对话
+ LangSmith Trace
```

## 第二阶段：多 Agent

```text
Supervisor
+ Planner
+ Executor
+ Reviewer
+ Summarizer
+ 数据库只读工具
+ HTTP API 工具
```

## 第三阶段：生产安全

```text
人工审批
+ Python 沙箱
+ 权限过滤
+ 审计日志
+ 重试与熔断
+ Checkpointer
+ Worker
```

## 第四阶段：质量工程

```text
LangSmith Dataset
+ 离线评估
+ RAG 指标
+ Agent 轨迹评估
+ Prompt 版本管理
+ 线上反馈闭环
```

---

# 十四、核心设计结论

这个项目不应设计成：

```text
一个 Agent + 所有工具 + 一个超长 Prompt
```

而应设计成：

```text
LangGraph 负责流程和状态
LangChain 负责模型、检索和工具抽象
专用 Agent 负责单一领域
工具层负责真实操作和安全校验
Reviewer 负责质量门禁
LangSmith 负责追踪、评估与监控
PostgreSQL Checkpointer 负责会话恢复
独立 Store 负责跨会话长期记忆
```

推荐先确定一个关键基础设施选型：**PostgreSQL + pgvector 单库方案**，还是 **PostgreSQL + Elasticsearch/OpenSearch 双存储方案**。前者适合快速落地和中等数据量，后者适合复杂全文检索、关键词精确查询和较大规模知识库。

[1]: https://docs.langchain.com/oss/python/langgraph/workflows-agents "Workflows and agents - Docs by LangChain"
[2]: https://docs.langchain.com/oss/python/langchain/retrieval "Retrieval - Docs by LangChain"
[3]: https://docs.langchain.com/oss/python/langgraph/application-structure "Application structure - Docs by LangChain"
[4]: https://docs.langchain.com/oss/python/langgraph/persistence "Persistence - Docs by LangChain"
[5]: https://docs.langchain.com/oss/python/langgraph/interrupts "Interrupts - Docs by LangChain"
[6]: https://docs.langchain.com/langsmith/observability "LangSmith Observability - Docs by LangChain"

# 企业级多智能体 RAG 项目



# 设计与开发指南

*Python · LangChain · LangGraph · LangSmith · Skills*

> 规划 · 执行 · 审核 · 总结  |  文档检索 · RAG · 多轮问答  |  数据库 · HTTP API · 搜索 · Python

| 文档版本 | V1.0 |
| --- | --- |
| 文档状态 | 架构基线 / 开发实施版 |
| 适用对象 | 架构师、后端开发、算法工程师、测试工程师、运维与安全人员 |
| 更新日期 | 2026-07-15 |
| 适用范围 | 企业知识库问答、智能分析、业务助手、研究与自动化执行场景 |



# 文档说明

本文档将前述的 LangChain、LangGraph、LangSmith、多 Agent、RAG、工具调用与 Skills 设计统一为一套可落地的工程方案。内容既可作为项目立项和架构评审材料，也可直接作为研发团队的开发指南。

> 说明｜版本适配：LangChain 生态更新较快。本文强调稳定的架构边界和工程方法，不强制绑定某个短期 API 细节。实施时应通过 pyproject.toml/uv.lock 锁定依赖，并在升级前查看官方 Changelog、运行离线评估与回归测试。



# 1. 项目概述

## 1.1 建设目标

建设一个以 LangGraph 为流程编排核心、以 LangChain 为模型与工具抽象层、以 LangSmith 为可观测与评估平台、以 Skills 为领域能力封装层的企业级智能体系统。系统支持文档检索、RAG、多轮问答、复杂任务规划、工具执行、结果审核、人工审批和最终总结。

- 面向内部知识库、制度、合同、技术文档、产品资料等内容提供可引用的问答。
- 将复合任务拆解为可执行步骤，由多个专用 Agent 协作完成。
- 安全调用数据库、HTTP API、公开搜索和隔离的 Python 运行环境。
- 通过 Checkpointer 保持会话状态，通过 Store 保存跨会话长期记忆。
- 通过 LangSmith 实现 Trace、质量评估、Prompt/模型对比、线上监控和反馈闭环。
- 通过文件化 Skills 按需加载领域流程、参考资料、脚本和模板，避免系统 Prompt 膨胀。

## 1.2 非目标与边界

- 不将一个“大 Agent”绑定全部工具后完全自由运行。生产系统采用受控路由、结构化计划、有限重试和审核门禁。
- 不允许 LLM 直接持有数据库管理员权限、任意 HTTP 访问权限或宿主机 Python 执行权限。
- 不将向量检索结果直接视为事实；答案必须经过来源、权限、时效和引用校验。
- 不以自然语言字符串作为核心系统接口；Agent、Skill、Tool 和 Graph 节点之间优先使用 Pydantic/TypedDict 结构化数据。

## 1.3 核心设计结论

**职责划分**

```text
LangGraph    = 流程、状态、路由、持久化、恢复、人工审批
LangChain    = 模型、消息、Prompt、Retriever、Tool、Middleware、结构化输出
Skills       = 可复用的领域流程、最佳实践、脚本、参考资料和模板
Agents       = 角色化决策单元
Tools        = 受约束的真实操作能力
Subgraphs    = 复杂 Skill 或专用 Agent 的独立流程
LangSmith    = Trace、调试、离线/在线评估、监控和反馈闭环
```



# 2. 总体架构

## 2.1 分层架构

**总体逻辑架构**

```text
┌──────────────────────────────────────────────────────────────┐
│ 客户端层：Web / 移动端 / 企业微信 / 钉钉 / API 调用方          │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTP / SSE / WebSocket
┌──────────────────────────────▼───────────────────────────────┐
│ 接入层：FastAPI、认证、租户、限流、会话、文件上传、流式输出    │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│ 编排层：LangGraph Supervisor / Planner / Executor / Reviewer │
│         Skill Selector / Skill Loader / Human Approval       │
└───────────────┬───────────────────────────────┬───────────────┘
                │                               │
┌───────────────▼──────────────┐  ┌────────────▼──────────────┐
│ 能力层：RAG/DB/HTTP/Search/  │  │ Skills：指令/工具/脚本/   │
│ Python/Summary 专用 Agents   │  │ Graph Skill               │
└───────────────┬──────────────┘  └────────────┬──────────────┘
                └──────────────────┬────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────┐
│ 工具与数据层：PostgreSQL/pgvector、Redis、对象存储、API、搜索 │
│               Python Sandbox、文档解析与异步 Worker          │
└──────────────────────────────────┬───────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────┐
│ 可观测层：LangSmith Trace、Evaluation、Dashboards、Alerts    │
└──────────────────────────────────────────────────────────────┘
```



## 2.2 推荐技术栈

| 领域 | 推荐组件 | 职责 |
| --- | --- | --- |
| API 服务 | FastAPI + Uvicorn/Gunicorn | HTTP、SSE/WebSocket、认证、请求校验和会话接口 |
| Agent 编排 | LangGraph | 状态机、条件路由、子图、持久化、流式事件、Interrupt |
| 模型与工具抽象 | LangChain | Chat Model、Tool、Retriever、Middleware、结构化输出 |
| 能力封装 | SKILL.md + Skill Registry | 按需加载流程、参考资料、脚本、模板和权限声明 |
| 可观测与评估 | LangSmith | Trace、数据集、离线/在线评估、监控和反馈 |
| 主数据库 | PostgreSQL | 业务数据、会话元数据、权限、文档元数据、审计记录 |
| 向量检索 | pgvector（初期） | Embedding 存储与语义检索；中大型场景可替换专用向量库 |
| 全文检索 | PostgreSQL FTS 或 OpenSearch | 关键词、编号、条款、精确字段和 BM25 检索 |
| 缓存与队列 | Redis | 缓存、限流、分布式锁、任务状态；队列可使用 Celery/RQ/Arq |
| 文件存储 | S3/MinIO | 原始文档、解析产物、导出文件和中间工件 |
| Python 执行 | 独立容器/沙箱服务 | 限制 CPU、内存、网络、文件和执行时间 |
| 依赖管理 | uv + pyproject.toml | 可复现安装、锁版本和开发工具统一管理 |

## 2.3 核心原则

- 单一职责：Agent 负责角色决策，Skill 负责领域流程，Tool 负责真实动作，Middleware 负责横切控制。
- 最小权限：最终可用能力是用户权限、Agent 权限、Skill 声明、环境策略和风险策略的交集。
- 显式状态：任务计划、检索文档、工具结果、审核结论和最终答案分别存储，不全部塞进 messages。
- 有限自治：最大步骤、重试、循环、Token、工具调用和总运行时间必须有上限。
- 可恢复：可能暂停、失败或等待人工输入的流程必须使用持久化 Checkpointer 和稳定 thread_id。
- 可评估：每个 Agent、Skill、Retriever、Tool 和 Prompt 均应具备可独立回归的评估数据集。
- 可替换：模型、向量库、Reranker、搜索供应商和数据库连接通过接口或工厂隔离。



# 3. 多 Agent 协作设计

## 3.1 Agent 清单与职责

| Agent | 主要职责 | 禁止事项 | 典型输出 |
| --- | --- | --- | --- |
| Supervisor | 意图识别、风险判断、路由、决定是否规划与审核 | 不直接执行复杂业务和高风险写操作 | RouteDecision |
| Planner | 将复杂目标拆解为有依赖关系的步骤 | 不直接操作数据库或外部系统 | ExecutionPlan |
| Executor | 调度步骤、选择专用 Agent/Skill、保存工件和状态 | 不绕过权限和审核 | StepExecutionResult |
| RAG Agent | 查询改写、混合检索、重排、上下文构建、引用回答 | 不伪造引用或跨权限检索 | RagAnswer |
| Database Agent | 理解业务指标、生成受控只读查询、解释结果 | 不直接获得管理员连接或执行任意 SQL | DatabaseAnalysisResult |
| HTTP Agent | 调用明确注册的业务 API、规范化响应 | 不提供任意 URL 请求能力 | ApiExecutionResult |
| Search Agent | 公开搜索、来源筛选、交叉验证和引用 | 不把单一搜索摘要直接视为事实 | ResearchResult |
| Python Agent | 数据处理、统计分析、图表和文件转换 | 不在 API 主进程执行任意代码 | PythonArtifactResult |
| Reviewer | 完整性、事实性、引用、工具结果和安全审核 | 不在无证据情况下直接“润色通过” | ReviewResult |
| Summarizer | 合并已审核材料、区分事实/推断/建议、形成最终回答 | 不引入未审核的新事实 | FinalResponse |

## 3.2 路由策略

**典型路由矩阵**

```text
简单闲聊 / 明确常识                 → direct_answer
内部文档、制度、合同、上传文件       → rag_agent
结构化业务数据、指标、报表           → database_agent
外部业务系统查询                     → http_agent
最新公开信息、竞品、新闻、研究       → search_agent
数据计算、文件分析、图表             → python_agent
多个数据源或有依赖关系的复合任务     → planner → executor
数据库写入、外部系统变更、发送行为   → human_approval
```

## 3.3 计划、执行、审核循环

复杂任务进入 Planner 后生成结构化计划。Executor 只执行当前可运行步骤，完成后更新状态；所有步骤完成后进入 Reviewer。Reviewer 可以通过、指定返工目标或要求人工审批，但不得形成无限循环。

| 控制项 | 建议默认值 | 说明 |
| --- | --- | --- |
| 最大规划步骤 | 8 | 超过时要求 Planner 合并步骤或分阶段执行 |
| 单步骤最大重试 | 2 | 仅对可重试异常执行；参数错误应先修正计划 |
| 审核返工次数 | 2 | 超过后返回部分结果和明确失败原因 |
| 单工具超时 | 15～60 秒 | 按数据库、HTTP、搜索、Python 分级配置 |
| Graph 总超时 | 业务配置 | 避免用户请求无限占用资源 |
| 并发步骤数 | 2～5 | 需考虑模型限流、数据库压力和外部 API 配额 |

## 3.4 Supervisor 输出模型

**结构化路由模型**

```python
from typing import Literal
from pydantic import BaseModel, Field

class RouteDecision(BaseModel):
    task_type: Literal[
        "direct_answer", "rag", "database", "http_api",
        "web_search", "python_analysis", "multi_step"
    ]
    target_agent: str
    candidate_skills: list[str] = Field(default_factory=list)
    needs_planning: bool = False
    needs_review: bool = True
    risk_level: Literal["low", "medium", "high"] = "low"
    reason: str
```



# 4. Skills 能力体系

## 4.1 Agent、Skill、Tool、Subgraph 的边界

| 概念 | 回答的问题 | 示例 |
| --- | --- | --- |
| Agent | 由谁负责判断和决策？ | RAG Agent、Database Agent、Reviewer |
| Skill | 完成该类任务应遵循什么标准流程？ | document-question-answering、database-analysis |
| Tool | 系统具体能够执行什么动作？ | knowledge_search、execute_readonly_sql、get_order |
| Subgraph | 复杂能力如何形成可恢复、可测试的流程？ | web-research graph、document-comparison graph |
| Prompt | 当前一次模型调用的指令和上下文是什么？ | 规划 Prompt、审核 Rubric、回答模板 |
| Middleware | 执行过程需要统一施加哪些控制？ | 限流、重试、PII、HITL、日志、Tool 过滤 |

## 4.2 Skill 包结构

**标准 Skill 目录**

```text
skills/
└── document-question-answering/
    ├── SKILL.md                  # YAML frontmatter + 执行说明
    ├── references/              # 业务规则、数据字典、引用规范
    │   ├── retrieval-policy.md
    │   └── citation-policy.md
    ├── scripts/                 # 确定性脚本和校验器
    │   └── validate_citations.py
    ├── assets/                  # 模板、示例、静态配置
    │   └── answer-template.md
    └── tests/                   # Skill 独立验收样例
        └── cases.yaml
```

## 4.3 SKILL.md 示例

**SKILL.md**

```markdown
---
name: document-question-answering
description: >
  对知识库文档进行检索和问答。用户询问内部制度、合同、
  产品手册、技术文档或上传文件内容时使用。
version: "1.0.0"
status: active
metadata:
  category: rag
  owner: knowledge-team
  risk-level: low
  timeout-seconds: 60
agents:
  - rag-agent
allowed-tools:
  - rewrite_query
  - knowledge_search
  - rerank_documents
  - build_citations
required-permissions:
  - knowledge_base.read
---

# 执行流程
1. 将多轮问题改写为独立问题，但保留用户的限定条件。
2. 在用户有权访问的知识库和文档范围内检索。
3. 执行向量检索与关键词检索，合并后重排。
4. 仅使用能够支持结论的文档片段回答。
5. 每个关键结论必须包含可追溯引用。
6. 证据不足时明确说明，不得补写不存在的条款。
```

## 4.4 Skill 类型

| 类型 | 适用场景 | 执行方式 |
| --- | --- | --- |
| Instruction Skill | 摘要、审核、问题改写、写作规范 | 加载指令和参考资料，由 Agent 执行 |
| Tool-backed Skill | 数据库分析、API 查询、RAG 组合流程 | 按 Skill 约束组合多个 Tool |
| Script Skill | SQL 校验、引用校验、格式转换、固定算法 | 运行经过审核的确定性脚本 |
| Graph Skill | 研究、文档对比、复杂分析、人工审批流程 | 编译为独立 LangGraph Subgraph |

## 4.5 Skill 发现与选择

建议采用两阶段选择：第一阶段根据 Agent、权限、标签、风险和环境进行规则召回；第二阶段让模型在少量候选 Skill 中进行结构化语义选择。启动时只加载 Skill 名称和描述，命中后再读取完整说明及必要的 references/scripts/assets。

**权限交集**

```text
最终可用工具 =
    Skill 声明工具
  ∩ Agent 允许工具
  ∩ 用户/租户权限工具
  ∩ 当前环境可用工具
  ∩ 风险与审批策略允许工具
```

> 说明｜避免 Skill 混淆：不要创建大量名称和描述高度重叠的 Skill，例如 document-search、knowledge-search、rag-search、document-qa。优先合并为边界明确的能力，并在 description 中写清“何时使用、何时不要使用、与相似 Skill 的区别”。

## 4.6 首批建议 Skills

| Skill | 归属 Agent | 核心能力 |
| --- | --- | --- |
| document-question-answering | RAG Agent | 检索、重排、引用回答 |
| document-comparison | RAG Agent | 跨文档/跨版本条款和差异比较 |
| knowledge-base-summary | RAG Agent | 按范围归纳知识库内容 |
| database-analysis | Database Agent | Schema 理解、只读查询和指标解释 |
| external-api-query | HTTP Agent | 按 API Contract 调用业务系统 |
| web-research | Search Agent | 搜索、抓取、来源筛选和交叉验证 |
| python-data-analysis | Python Agent | 统计、文件处理和图表工件 |
| task-planning | Planner | 任务拆解、依赖和计划修复 |
| result-review | Reviewer | 事实、引用、完整性和安全审核 |
| final-summary | Summarizer | 多来源材料汇总和最终表达 |



# 5. LangGraph 状态与工作流

## 5.1 State 设计原则

- State 是节点之间的业务协议，不是任意对象存储箱。字段必须有清晰所有者和更新规则。
- messages 只保存对话消息；计划、检索结果、工件、审核和最终答案使用独立字段。
- 大型二进制文件、完整文档和完整 SKILL.md 不写入 Checkpoint，只保存对象存储地址、ID、版本和 Hash。
- 每个节点只返回其负责修改的字段，避免复制和覆盖整个 State。
- 并行节点写入同一字段时必须定义 reducer，或改为按 step_id/agent_id 分区存储。

## 5.2 核心 State 示例

**state.py**

```python
from typing import Annotated, Any, Literal
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class PlanStep(TypedDict):
    id: str
    agent: str
    skill: str | None
    action: str
    depends_on: list[str]
    status: Literal["pending", "running", "completed", "failed"]
    retries: int
    result_key: str | None

class AgentState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    user_id: str
    tenant_id: str
    thread_id: str
    conversation_id: str

    original_query: str
    standalone_query: str
    route: dict[str, Any]

    plan: list[PlanStep]
    current_step_id: str | None
    artifacts: dict[str, Any]
    tool_results: list[dict[str, Any]]

    available_skills: list[dict[str, Any]]
    selected_skills: list[dict[str, Any]]
    active_skill: dict[str, Any] | None
    skill_results: dict[str, Any]

    knowledge_base_ids: list[str]
    retrieved_documents: list[dict[str, Any]]
    citations: list[dict[str, Any]]

    draft_answer: str
    review: dict[str, Any]
    retry_count: int
    max_retries: int

    requires_human_approval: bool
    error: dict[str, Any] | None
    final_answer: str
```

## 5.3 主 Graph 流程

**主流程**

```text
START
  ↓
load_context
  ↓
supervisor
  ↓
resolve_agent
  ↓
discover_skills → select_skills → load_and_validate_skill
  ↓
needs_plan?
  ├─ 否 → execute_skill
  └─ 是 → planner → executor ─┐
                              │ 未完成步骤
                              └─────────────┘
  ↓
reviewer
  ├─ passed     → summarizer → finalize → END
  ├─ retryable  → 指定目标节点（最多有限次数）
  ├─ approval   → human_approval → 恢复执行
  └─ failed     → error_handler → 部分结果/明确错误 → END
```

## 5.4 Subgraph 使用规则

复杂 Skill 或独立团队维护的能力可实现为 Subgraph。父图与子图共享状态字段时，可直接将编译后的子图作为节点；状态 Schema 不同或需要隔离消息历史时，使用包装节点完成输入输出转换。

- RAG Subgraph：query_rewrite → retrieve → rerank → context_build → answer → citation_check。
- Web Research Subgraph：query_plan → parallel_search → fetch → source_filter → synthesize。
- Python Analysis Subgraph：inspect_input → plan_code → approval(optional) → sandbox_execute → validate_artifact。
- 每个 Subgraph 定义稳定的输入输出 Schema，不允许父图依赖其内部节点实现。

## 5.5 Interrupt 与人工审批

| 需要审批的操作 | 审批展示内容 | 恢复后动作 |
| --- | --- | --- |
| 数据库写入 | SQL、影响表、预计影响行数、回滚信息 | 使用幂等事务执行并记录审计 |
| 外部 API 变更 | 接口、参数、目标对象、风险和幂等键 | 调用指定 API 并回写结果 |
| 发送邮件/消息 | 收件人、正文、附件、业务原因 | 发送后记录外部消息 ID |
| Python 高风险执行 | 代码摘要、输入文件、网络/文件权限 | 在沙箱中恢复执行 |
| 敏感数据导出 | 字段、范围、数量、脱敏策略 | 生成受控下载工件 |

> 重要｜Interrupt 规则：Interrupt 之前可能重复执行的副作用必须幂等；恢复时复用相同 thread_id。中断载荷应为可 JSON 序列化的简单结构，不要传递数据库连接、文件句柄或复杂运行时对象。



# 6. 文档检索与 RAG 设计

## 6.1 文档入库流程

**入库 Pipeline**

```text
上传 / 同步文档
  ↓
文件类型、大小、病毒和权限检查
  ↓
解析 PDF / DOCX / HTML / Markdown / Excel / PPTX
  ↓
文本清洗、版面结构识别、表格与图片处理
  ↓
按标题、段落、列表、表格进行语义切分
  ↓
补充 metadata、ACL、版本、Hash
  ↓
去重与增量判断
  ↓
Embedding + 全文索引
  ↓
写入 Vector Store、Document Store 和关系表
  ↓
抽样验证、质量报告、发布知识库版本
```

## 6.2 Chunk 元数据

**推荐 metadata**

```json
{
  "chunk_id": "uuid",
  "document_id": "uuid",
  "knowledge_base_id": "uuid",
  "tenant_id": "tenant-a",
  "content": "...",
  "page_number": 12,
  "section_path": ["第三章", "3.2 权限管理"],
  "source_name": "系统设计说明书.pdf",
  "source_uri": "s3://bucket/...",
  "content_hash": "sha256:...",
  "document_version": 3,
  "language": "zh-CN",
  "content_type": "paragraph",
  "access_scope": ["department:technology"],
  "valid_from": null,
  "valid_to": null
}
```

## 6.3 检索流程

**Hybrid RAG**

```text
多轮问题改写为独立查询
  ↓
识别实体、编号、时间范围、文档范围和权限过滤
  ↓
Vector Search Top K   +   BM25/全文检索 Top K
  ↓                         ↓
            合并、去重、RRF 融合
                       ↓
                Reranker Top N
                       ↓
           上下文压缩与引用片段构建
                       ↓
              Grounded Answer 生成
                       ↓
           引用一致性和证据充分性审核
```

## 6.4 RAG 策略建议

| 问题类型 | 优先策略 | 原因 |
| --- | --- | --- |
| 自然语言概念问题 | 向量检索 + Rerank | 语义相似性更重要 |
| 合同编号、错误码、产品型号 | 关键词/全文检索优先 | 精确字符匹配更可靠 |
| 制度条款和原文定位 | 全文检索 + 页码/章节过滤 | 需要精确引用原文 |
| 跨文档比较 | 按文档分组检索 + 对齐字段 | 避免一个文档占据全部 Top K |
| 时间敏感内容 | 版本和有效期过滤 | 避免引用已失效制度 |
| 多租户/部门知识 | ACL 前置过滤 | 权限必须在检索阶段生效 |

## 6.5 答案与引用规范

- 每条引用至少包含 document_id、chunk_id、文件名、页码/章节和引用文本 Hash。
- 关键结论应能映射到一条或多条引用；引用只“相关”但不能支持结论时不得使用。
- 证据不足、文档互相冲突、版本不明时，应明确说明不确定性并列出冲突来源。
- 回答中区分“文档明确记载”“根据数据推断”“系统建议”三类表达。
- 不要让模型自行拼接不可验证的页码或来源链接；引用由代码根据检索 metadata 构建。



# 7. Tool 体系与外部能力接入

## 7.1 Tool 设计规范

每个 Tool 是输入输出明确、权限可校验、可追踪、可超时和可重试的服务函数。Tool 名称应稳定且简洁，输入使用 Pydantic Schema，返回统一 ToolResult，异常不得直接泄露连接串、密钥或内部堆栈。

**统一 Tool 返回模型**

```python
from typing import Any, Literal
from pydantic import BaseModel, Field

class ToolError(BaseModel):
    code: str
    message: str
    retryable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)

class ToolResult(BaseModel):
    status: Literal["success", "partial", "failed"]
    data: Any = None
    error: ToolError | None = None
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
```

## 7.2 Tool Registry

**registry.py**

```python
from dataclasses import dataclass
from collections.abc import Callable

@dataclass(frozen=True)
class ToolDefinition:
    name: str
    handler: Callable
    risk_level: str
    requires_approval: bool
    timeout_seconds: int
    allowed_agents: tuple[str, ...]
    required_permissions: tuple[str, ...]

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        if definition.name in self._tools:
            raise ValueError(f"Duplicate tool: {definition.name}")
        self._tools[definition.name] = definition

    def resolve(self, *, agent: str, permissions: set[str]):
        return [
            t for t in self._tools.values()
            if agent in t.allowed_agents
            and set(t.required_permissions).issubset(permissions)
        ]
```

## 7.3 数据库 Tool

| 控制项 | 要求 |
| --- | --- |
| 连接账户 | 默认使用只读账户；写操作使用独立账户和审批流程 |
| SQL 校验 | 解析 AST，禁止多语句、DDL、DML、危险函数和未授权 Schema |
| 表字段白名单 | Agent 仅看到其业务域所需的 Schema 摘要 |
| 行数与超时 | 自动追加/校验 LIMIT，设置 statement_timeout |
| 敏感字段 | 在数据库或 Tool 层脱敏，禁止将明文交给模型 |
| 审计 | 记录用户、Agent、Skill、SQL Hash、参数、耗时和影响范围 |
| 结果大小 | 大结果写入对象存储，只把摘要和工件地址返回 State |

## 7.4 HTTP API Tool

- 不要向模型暴露通用 requests(url, method, body) 工具；每个业务动作封装成明确函数。
- 域名、路径、方法、请求参数和响应 Schema 通过服务端配置或 OpenAPI Contract 固定。
- 认证 Token 由服务端注入，不进入 Prompt、State、Trace 或 Tool 参数。
- 写操作必须支持幂等键，并在重试前确认上次调用是否已成功。
- 限制响应体大小，必要时只保留白名单字段或将原始响应写入受控工件。
- 区分 4xx 参数/权限错误与 5xx/网络可重试错误，禁止盲目重试所有异常。

## 7.5 搜索与网页读取 Tool

- 搜索结果只作为候选来源，需进行页面读取、发布日期判断、来源评级和多来源验证。
- 对公开网页设置域名策略、抓取超时、robots/条款合规、最大页面大小和内容类型限制。
- 将网页正文、标题、URL、发布日期、抓取时间和内容 Hash 一并保存，便于复现。
- 搜索类回答必须区分事件发生日期与页面发布日期。

## 7.6 Python 沙箱

| 资源/权限 | 建议 |
| --- | --- |
| CPU | 单任务配额与硬超时 |
| 内存 | 容器级限制，避免读取超大文件导致 OOM |
| 文件系统 | 只读基础镜像 + 任务独立临时目录 + 输出目录白名单 |
| 网络 | 默认关闭；确需访问时只允许明确域名 |
| 模块 | 使用依赖白名单或预构建分析镜像 |
| 进程 | 禁止 fork bomb、后台守护进程和无限子进程 |
| 结果 | stdout/stderr 限长，文件工件扫描后上传对象存储 |



# 8. 多轮会话、记忆与持久化

## 8.1 Checkpointer 与 Store

| 机制 | 范围 | 适用内容 |
| --- | --- | --- |
| Checkpointer | 单个 thread | Graph 状态、消息、计划、Interrupt、故障恢复、时间旅行 |
| Store | 跨 thread | 用户偏好、长期事实、已确认配置、共享知识和用户画像 |
| 业务数据库 | 业务实体 | 会话索引、文档、权限、反馈、任务和审计记录 |
| 对象存储 | 大文件/工件 | 原始文档、解析结果、导出文件、图表和大型 Tool 输出 |

## 8.2 长对话压缩

**对话压缩规则**

```text
当消息或 Token 达到阈值：
1. 提取 confirmed_facts、decisions、user_goal、unresolved_questions。
2. 保留最近 N 轮原始消息。
3. 将旧 Tool 原始输出替换为结构化摘要和 artifact_id。
4. 摘要写入 State；稳定偏好和事实经校验后写入 Store。
5. 不删除仍被当前计划引用的证据、审批信息和错误上下文。
```

## 8.3 thread_id 规范

- 使用 UUID 或长度受控的稳定 ID；不要把长业务描述直接拼入 thread_id。
- 同一会话恢复、中断继续和流式重连必须复用 thread_id。
- 新建分支任务时创建新 thread_id，并在业务表记录 parent_thread_id。
- 生产环境使用持久化 Checkpointer；内存 Checkpointer 仅用于单元测试和本地实验。
- 设置 Checkpoint 保留策略，避免长会话无限增长。



# 9. 推荐项目结构

以下目录按“接口层、编排层、Agent、Skills、RAG、Tools、领域、基础设施、服务与测试”拆分。实际项目可根据团队规模合并，但不建议将 Graph 节点、工具实现和 API 路由全部放在同一模块。

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
├── alembic.ini
├── src/
│   └── enterprise_agent/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── dependencies.py
│       │   ├── middleware.py
│       │   ├── exception_handlers.py
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
│       ├── graph/
│       │   ├── builder.py
│       │   ├── state.py
│       │   ├── context.py
│       │   ├── routing.py
│       │   ├── events.py
│       │   └── nodes/
│       │       ├── load_context.py
│       │       ├── supervisor.py
│       │       ├── skill_discovery.py
│       │       ├── skill_selector.py
│       │       ├── skill_loader.py
│       │       ├── planner.py
│       │       ├── executor.py
│       │       ├── reviewer.py
│       │       ├── human_approval.py
│       │       ├── summarizer.py
│       │       ├── error_handler.py
│       │       └── finalize.py
│       ├── agents/
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
│       ├── skills/
│       │   ├── core/
│       │   │   ├── models.py
│       │   │   ├── protocols.py
│       │   │   ├── enums.py
│       │   │   └── exceptions.py
│       │   ├── registry/
│       │   │   ├── registry.py
│       │   │   ├── discovery.py
│       │   │   ├── loader.py
│       │   │   ├── resolver.py
│       │   │   └── cache.py
│       │   ├── selection/
│       │   │   ├── selector.py
│       │   │   ├── rule_selector.py
│       │   │   ├── semantic_selector.py
│       │   │   ├── ranking.py
│       │   │   └── conflict_resolver.py
│       │   ├── execution/
│       │   │   ├── executor.py
│       │   │   ├── context_builder.py
│       │   │   ├── prompt_executor.py
│       │   │   ├── script_executor.py
│       │   │   ├── graph_executor.py
│       │   │   └── result_adapter.py
│       │   ├── validation/
│       │   │   ├── manifest_validator.py
│       │   │   ├── dependency_validator.py
│       │   │   ├── tool_validator.py
│       │   │   ├── security_validator.py
│       │   │   └── output_validator.py
│       │   ├── policies/
│       │   │   ├── access_policy.py
│       │   │   ├── execution_policy.py
│       │   │   ├── approval_policy.py
│       │   │   ├── resource_policy.py
│       │   │   └── version_policy.py
│       │   └── lifecycle/
│       │       ├── publisher.py
│       │       ├── versioning.py
│       │       ├── installer.py
│       │       └── deprecation.py
│       ├── skill_packages/
│       │   ├── document-question-answering/
│       │   │   ├── SKILL.md
│       │   │   ├── references/
│       │   │   ├── scripts/
│       │   │   ├── assets/
│       │   │   └── tests/
│       │   ├── document-comparison/
│       │   ├── database-analysis/
│       │   ├── external-api-query/
│       │   ├── web-research/
│       │   ├── python-data-analysis/
│       │   ├── task-planning/
│       │   ├── result-review/
│       │   └── final-summary/
│       ├── rag/
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
│       │   │   ├── context_builder.py
│       │   │   ├── answer_generator.py
│       │   │   └── citation_builder.py
│       │   └── evaluation/
│       │       ├── retrieval_quality.py
│       │       ├── groundedness.py
│       │       └── citation_correctness.py
│       ├── tools/
│       │   ├── registry.py
│       │   ├── policies.py
│       │   ├── result.py
│       │   ├── database/
│       │   │   ├── read_sql.py
│       │   │   ├── schema_inspector.py
│       │   │   └── query_validator.py
│       │   ├── http/
│       │   │   ├── client.py
│       │   │   ├── allowlist.py
│       │   │   └── api_tools.py
│       │   ├── search/
│       │   │   ├── web_search.py
│       │   │   ├── page_reader.py
│       │   │   └── source_ranker.py
│       │   ├── python/
│       │   │   ├── client.py
│       │   │   ├── sandbox.py
│       │   │   └── serializers.py
│       │   └── documents/
│       │       └── knowledge_search.py
│       ├── memory/
│       │   ├── conversation.py
│       │   ├── short_term.py
│       │   ├── long_term.py
│       │   ├── summarization.py
│       │   └── profile_store.py
│       ├── llm/
│       │   ├── factory.py
│       │   ├── models.py
│       │   ├── fallback.py
│       │   ├── structured.py
│       │   ├── token_counter.py
│       │   └── rate_limiter.py
│       ├── prompts/
│       │   ├── supervisor.py
│       │   ├── planner.py
│       │   ├── rag.py
│       │   ├── database.py
│       │   ├── reviewer.py
│       │   └── summarizer.py
│       ├── domain/
│       │   ├── entities/
│       │   ├── enums.py
│       │   └── exceptions.py
│       ├── repositories/
│       │   ├── conversation_repository.py
│       │   ├── document_repository.py
│       │   ├── knowledge_base_repository.py
│       │   ├── execution_repository.py
│       │   └── feedback_repository.py
│       ├── services/
│       │   ├── chat_service.py
│       │   ├── ingestion_service.py
│       │   ├── knowledge_base_service.py
│       │   ├── approval_service.py
│       │   └── evaluation_service.py
│       ├── workers/
│       │   ├── document_tasks.py
│       │   ├── embedding_tasks.py
│       │   └── evaluation_tasks.py
│       ├── infrastructure/
│       │   ├── database/
│       │   │   ├── session.py
│       │   │   ├── models.py
│       │   │   └── migrations/
│       │   ├── vectorstore/pgvector_store.py
│       │   ├── cache/redis.py
│       │   ├── checkpoint/postgres.py
│       │   ├── object_storage/s3.py
│       │   ├── queue/task_queue.py
│       │   ├── skills/filesystem_store.py
│       │   └── observability/
│       │       ├── langsmith.py
│       │       ├── logging.py
│       │       └── metrics.py
│       ├── config/
│       │   ├── settings.py
│       │   ├── logging.py
│       │   └── constants.py
│       └── utils/
│           ├── ids.py
│           ├── retry.py
│           ├── serialization.py
│           └── timing.py
├── tests/
│   ├── unit/
│   │   ├── graph/
│   │   ├── agents/
│   │   ├── skills/
│   │   ├── rag/
│   │   └── tools/
│   ├── integration/
│   │   ├── test_graph_execution.py
│   │   ├── test_rag_pipeline.py
│   │   ├── test_skill_tool_binding.py
│   │   ├── test_skill_permissions.py
│   │   └── test_database_tools.py
│   ├── e2e/
│   │   └── test_chat_api.py
│   ├── evaluations/
│   │   ├── datasets/
│   │   ├── test_retrieval_quality.py
│   │   ├── test_groundedness.py
│   │   ├── test_agent_trajectory.py
│   │   ├── test_skill_selection.py
│   │   └── test_version_regression.py
│   └── fixtures/
├── scripts/
│   ├── init_database.py
│   ├── ingest_documents.py
│   ├── rebuild_index.py
│   ├── validate_skills.py
│   ├── run_evaluation.py
│   └── export_langsmith_dataset.py
├── alembic/
│   ├── env.py
│   └── versions/
└── docs/
    ├── architecture.md
    ├── graph-flow.md
    ├── rag-design.md
    ├── skills-guide.md
    ├── tool-security.md
    ├── evaluation.md
    └── deployment.md
```

## 9.1 目录边界说明

| 目录 | 只负责 | 不应负责 |
| --- | --- | --- |
| api/ | 协议、认证、校验、序列化、流式响应 | 业务流程、SQL、Prompt 和向量检索细节 |
| graph/ | State、节点、边、路由、Graph 编译 | 具体数据库驱动和外部 API 认证 |
| agents/ | 角色定义、模型调用和结构化决策 | 直接维护数据库连接或对象存储 |
| skills/ | Skill 注册、选择、加载、执行策略 | 把所有业务逻辑写成一个 loader |
| skill_packages/ | 可版本化的 SKILL.md 和资源 | 运行时密钥和环境专属连接信息 |
| rag/ | 入库、索引、检索、重排、引用 | HTTP 路由和 UI 格式 |
| tools/ | 真实动作的受控适配器 | 决定宏观任务流程 |
| services/ | 面向用例的应用服务 | 底层 SDK 初始化细节 |
| infrastructure/ | 数据库、缓存、存储、队列、观测实现 | 领域判断和 Prompt |



# 10. 核心代码骨架

## 10.1 Graph Builder

**graph/builder.py**

```python
from langgraph.graph import StateGraph, START, END
from enterprise_agent.graph.state import AgentState


def build_graph(*, checkpointer, store):
    builder = StateGraph(AgentState)

    builder.add_node("load_context", load_context)
    builder.add_node("supervisor", supervisor)
    builder.add_node("skill_selector", skill_selector)
    builder.add_node("planner", planner)
    builder.add_node("executor", executor)
    builder.add_node("reviewer", reviewer)
    builder.add_node("human_approval", human_approval)
    builder.add_node("summarizer", summarizer)
    builder.add_node("error_handler", error_handler)

    builder.add_edge(START, "load_context")
    builder.add_edge("load_context", "supervisor")
    builder.add_edge("supervisor", "skill_selector")
    builder.add_conditional_edges("skill_selector", route_after_skill_selection)
    builder.add_conditional_edges("planner", route_after_planning)
    builder.add_conditional_edges("executor", route_after_execution)
    builder.add_conditional_edges("reviewer", route_after_review)
    builder.add_edge("summarizer", END)
    builder.add_edge("error_handler", END)

    return builder.compile(checkpointer=checkpointer, store=store)


graph = build_graph(checkpointer=get_checkpointer(), store=get_store())
```

## 10.2 Node 约定

**节点接口规范**

```python
from collections.abc import Awaitable, Callable
from enterprise_agent.graph.state import AgentState

Node = Callable[[AgentState], Awaitable[dict]]

# 约定：
# 1. 节点接收完整 State，但只返回自身负责的字段更新。
# 2. 所有外部调用设置 timeout，并把错误映射为统一 ErrorInfo。
# 3. 节点不得将密钥、数据库连接或大型原始数据写入 State。
# 4. LLM 输出必须经过 Pydantic 校验；失败时执行有限修复或明确失败。
# 5. 对可能重复执行的副作用使用幂等键。
```

## 10.3 Planner 模型

**planner/models.py**

```python
from pydantic import BaseModel, Field

class PlanStepModel(BaseModel):
    id: str
    title: str
    agent: str
    skill: str | None = None
    action: str
    depends_on: list[str] = Field(default_factory=list)
    expected_output: str
    risk_level: str = "low"

class ExecutionPlan(BaseModel):
    goal: str
    assumptions: list[str] = Field(default_factory=list)
    steps: list[PlanStepModel]
    success_criteria: list[str]
    requires_human_approval: bool = False
```

## 10.4 Reviewer 模型

**reviewer/models.py**

```python
from typing import Literal
from pydantic import BaseModel, Field

class ReviewIssue(BaseModel):
    category: Literal[
        "missing_step", "unsupported_claim", "bad_citation",
        "tool_error", "security", "format", "other"
    ]
    severity: Literal["low", "medium", "high"]
    message: str
    retry_target: str | None = None

class ReviewResult(BaseModel):
    decision: Literal["pass", "retry", "approval", "fail"]
    score: float
    issues: list[ReviewIssue] = Field(default_factory=list)
    revised_instruction: str | None = None
```

## 10.5 langgraph.json

**langgraph.json**

```json
{
  "dependencies": ["."],
  "graphs": {
    "enterprise_agent": "./src/enterprise_agent/graph/builder.py:graph"
  },
  "env": ".env"
}
```



# 11. 开发环境与启动指南

## 11.1 前置要求

| 组件 | 用途 | 要求 |
| --- | --- | --- |
| Python | 项目运行时 | 选择团队统一支持版本，并在 CI 和生产保持一致 |
| uv | 依赖与虚拟环境 | 提交 uv.lock，禁止生产环境浮动安装 |
| Docker | PostgreSQL、Redis、MinIO、沙箱和本地集成环境 | 开发机和 CI 使用相同基础服务版本 |
| PostgreSQL | 业务、Checkpoint、向量和审计 | 启用 pgvector；生产配置备份、连接池和权限隔离 |
| LangSmith | Trace 和评估 | 配置独立 dev/staging/prod Project |

## 11.2 初始化步骤

**本地初始化命令**

```bash
# 1. 创建项目
mkdir enterprise-agent && cd enterprise-agent
uv init --package

# 2. 添加核心依赖（名称和版本以实施时官方文档为准）
uv add langchain langgraph langsmith fastapi uvicorn pydantic-settings
uv add sqlalchemy asyncpg psycopg[binary] pgvector alembic redis httpx
uv add --dev pytest pytest-asyncio ruff mypy

# 3. 启动本地基础服务
docker compose up -d postgres redis minio

# 4. 初始化数据库
uv run alembic upgrade head
uv run python scripts/init_database.py

# 5. 校验 Skills
uv run python scripts/validate_skills.py

# 6. 启动 API
uv run uvicorn enterprise_agent.main:app --reload

# 7. 启动文档 Worker（示例）
uv run python -m enterprise_agent.workers.document_tasks
```

## 11.3 环境变量

**.env.example**

```dotenv
APP_ENV=development
APP_NAME=enterprise-agent
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/agent
REDIS_URL=redis://localhost:6379/0
OBJECT_STORAGE_ENDPOINT=http://localhost:9000
OBJECT_STORAGE_BUCKET=agent-artifacts

LLM_PROVIDER=your_provider
LLM_MODEL=your_model
EMBEDDING_MODEL=your_embedding_model
RERANK_MODEL=your_rerank_model

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=***
LANGSMITH_PROJECT=enterprise-agent-dev

GRAPH_MAX_STEPS=8
GRAPH_MAX_RETRIES=2
TOOL_DEFAULT_TIMEOUT_SECONDS=30
PYTHON_SANDBOX_URL=http://sandbox:8080

SKILL_ROOTS=./src/enterprise_agent/skill_packages
SKILL_CACHE_TTL_SECONDS=300
```

## 11.4 开发顺序

1. 第一阶段：实现单知识库 RAG 闭环，包括上传、解析、切分、索引、检索、引用和多轮问答。
2. 第二阶段：加入 Supervisor、Planner、Executor、Reviewer 和 Summarizer，建立受控多 Agent 流程。
3. 第三阶段：加入 Skill Registry、首批 SKILL.md、Tool 权限交集和 Graph Skill。
4. 第四阶段：接入数据库、HTTP、搜索与 Python 沙箱，并为高风险操作加入 Interrupt。
5. 第五阶段：完善 LangSmith 数据集、离线评估、线上评估、监控告警和用户反馈闭环。
6. 第六阶段：压测、故障演练、权限审计、成本优化和生产发布。



# 12. 扩展开发指南

## 12.1 新增一个 Agent

1. 定义职责、输入、输出、允许的 Skill 和禁止事项，确认是否确实需要独立 Agent。
2. 创建结构化输出模型和 Prompt，禁止依赖自由文本解析关键字段。
3. 在 Agent Registry 注册模型、Tools、Middleware、超时和权限。
4. 根据复杂度决定作为普通节点还是独立 Subgraph。
5. 在 Supervisor 路由模型中增加目标类型，并补充正例、反例评估集。
6. 添加单元测试、路径集成测试、LangSmith 离线实验和成本基线。

## 12.2 新增一个 Skill

1. 创建独立目录和 SKILL.md，name 使用稳定的 kebab-case，description 写清激活边界。
2. 声明版本、状态、Agent、允许工具、所需权限、风险级别和超时。
3. 将大段背景资料放入 references，将确定性逻辑放入 scripts，将模板放入 assets。
4. 运行 manifest、路径、工具、权限和安全校验，禁止目录越界引用。
5. 为 Skill Selector 添加“应命中”和“不应命中”样例。
6. 为 Skill 输出定义 Schema 和验收标准，并记录 Skill 版本与内容 Hash。
7. 复杂 Skill 实现为 Subgraph，独立测试后再注册到主图。

## 12.3 新增一个 Tool

1. 从业务动作而不是底层通用能力命名，例如 get_order_status，而不是 request_url。
2. 使用 Pydantic 定义输入，字段说明应足够让模型正确选择和填参。
3. 返回统一 ToolResult；明确 retryable、错误码、工件和审计 metadata。
4. 配置 Agent 白名单、Skill 白名单、用户权限、风险等级、审批和超时。
5. 实现幂等、重试、熔断、限流和日志脱敏；敏感信息不进入 Trace。
6. 使用模拟服务完成单元测试，再使用测试环境完成集成测试。

## 12.4 新增知识库数据源

- 实现 Loader，将源数据转换为统一 Document 对象和标准 metadata。
- 定义同步游标、增量规则、删除传播、版本、权限和去重策略。
- 为特殊内容定义解析器，例如 Excel 表格、PPT 图文、扫描 PDF、代码仓库。
- 构建小规模黄金数据集，验证解析完整率、检索 Recall 和引用定位。
- 发布前运行权限穿透测试，确保无跨租户或跨部门文档泄露。



# 13. API 与数据模型建议

## 13.1 主要 API

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| POST | /v1/chat/stream | 发起对话并通过 SSE/WebSocket 流式返回事件 |
| POST | /v1/chat/invoke | 非流式执行，适合系统集成和测试 |
| GET | /v1/conversations/{id} | 读取会话及状态摘要 |
| POST | /v1/approvals/{id}/decision | 批准、拒绝或修改 Interrupt 请求 |
| POST | /v1/documents | 上传文档并创建入库任务 |
| GET | /v1/documents/{id} | 查询解析、索引和发布状态 |
| POST | /v1/knowledge-bases | 创建知识库 |
| POST | /v1/knowledge-bases/{id}/reindex | 重建或增量索引 |
| POST | /v1/feedback | 提交用户评分、纠错和引用反馈 |
| GET | /health/live\|ready | 存活和依赖就绪检查 |

## 13.2 流式事件模型

**SSE 事件示例**

```text
event: node_started
data: {"node":"rag_agent","run_id":"..."}

event: tool_started
data: {"tool":"knowledge_search","step_id":"step_2"}

event: retrieval
 data: {"documents":[...],"count":6}

event: token
 data: {"text":"根据制度文件..."}

event: approval_required
 data: {"approval_id":"...","summary":"准备执行数据库更新"}

event: completed
 data: {"answer":"...","citations":[...],"trace_id":"..."}
```

## 13.3 核心数据库表

| 表 | 关键字段 | 用途 |
| --- | --- | --- |
| tenants/users/roles | tenant_id、user_id、role、permissions | 租户、身份和权限 |
| conversations/messages | conversation_id、thread_id、role、content | 会话索引和消息展示 |
| executions/steps | run_id、step_id、agent、skill、status、latency | 执行轨迹和业务审计 |
| approvals | approval_id、payload、decision、operator | 人工审批 |
| knowledge_bases | id、tenant_id、name、status、version | 知识库管理 |
| documents/document_versions | document_id、version、hash、source_uri | 文档版本和生命周期 |
| chunks | chunk_id、document_id、content、metadata、embedding | 检索内容和向量 |
| skills/skill_versions（可选） | name、version、hash、status、owner | 动态 Skill 管理和发布 |
| feedback | run_id、score、category、comment | 用户反馈和评估数据 |
| audit_logs | actor、action、resource、result、timestamp | 安全和合规审计 |



# 14. LangSmith 可观测与评估

## 14.1 Trace 层级

**建议 Trace 结构**

```text
graph_run
├── load_context
├── supervisor
├── skill_selector
├── planner
├── executor
│   ├── rag_agent
│   │   ├── query_rewrite
│   │   ├── vector_search
│   │   ├── keyword_search
│   │   ├── reranker
│   │   └── answer_generation
│   ├── database_tool
│   ├── http_tool
│   └── python_sandbox
├── reviewer
└── summarizer
```

## 14.2 Trace metadata

**推荐 metadata**

```json
{
  "environment": "staging",
  "tenant_id": "tenant-a",
  "user_id_hash": "...",
  "conversation_id": "...",
  "thread_id": "...",
  "task_type": "multi_step",
  "agent": "rag_agent",
  "skill_name": "document-question-answering",
  "skill_version": "1.0.0",
  "knowledge_base_ids": ["kb-1"],
  "model_profile": "balanced",
  "release": "2026.07.15.1"
}
```

## 14.3 评估指标

| 层级 | 指标 |
| --- | --- |
| 路由/规划 | Agent Routing Accuracy、Plan Completeness、Dependency Correctness |
| Skills | Skill Selection Accuracy、Activation Recall、Completion Rate、Version Regression |
| RAG | Retrieval Recall@K、MRR/NDCG、Context Relevance、Groundedness、Citation Correctness |
| Tools | Tool Selection Accuracy、Argument Validity、Success Rate、Retry Rate、Side-effect Safety |
| 最终回答 | Task Completion、Factuality、Format、Helpfulness、Policy Compliance |
| 运行质量 | Latency、Token、Cost、Timeout、Loop Count、Error Rate、Approval Rate |

## 14.4 离线与在线评估流程

**评估闭环**

```text
开发阶段：
黄金数据集 → 运行候选版本 → Code/LLM/Human Evaluators
→ 与基线对比 → 回归门禁 → 合并发布

生产阶段：
真实 Trace → 采样在线 Evaluator → Dashboard/Alert
→ 失败 Trace 入队人工标注 → 加入离线数据集
→ 修复 → 重新实验 → 灰度发布
```

## 14.5 数据集分类

- 路由数据集：问题、正确 Agent、正确 Skill、是否规划、是否审批。
- RAG 数据集：问题、相关文档/Chunk、参考答案、必须引用和不应引用内容。
- 工具数据集：用户意图、正确 Tool、参数、模拟响应和错误场景。
- 轨迹数据集：期望节点路径、最大调用次数、禁止路径和终止条件。
- 安全数据集：Prompt Injection、越权查询、敏感字段、任意 URL、危险 SQL 和恶意文件。



# 15. 测试策略

## 15.1 测试金字塔

| 测试层 | 测试对象 | 特点 |
| --- | --- | --- |
| 单元测试 | 节点、选择器、校验器、Splitter、Tool 适配器 | 快、无外部依赖、覆盖边界和错误 |
| 组件测试 | Retriever、Skill Executor、Agent 结构化输出 | 使用固定模型响应或 Mock |
| 集成测试 | PostgreSQL、Redis、向量库、API、Sandbox | Docker 环境，验证真实协议 |
| Graph 路径测试 | 条件边、循环、Interrupt、恢复和错误分支 | 断言节点路径和 State 变化 |
| 端到端测试 | 上传文档 → 提问 → 引用 → 审批 → 结果 | 少量关键业务链路 |
| 评估测试 | RAG、路由、Skill、事实和轨迹质量 | 统计指标和发布门禁 |
| 安全测试 | 越权、注入、SSRF、SQL、文件和数据泄露 | 红队样例和自动扫描 |

## 15.2 Graph 节点测试

**节点测试示例**

```python
@pytest.mark.asyncio
async def test_reviewer_retries_unsupported_claim():
    state = make_state(
        draft_answer="制度明确允许无限期远程办公",
        citations=[],
        retry_count=0,
        max_retries=2,
    )
    update = await reviewer(state)

    assert update["review"]["decision"] == "retry"
    assert update["review"]["issues"][0]["category"] == "unsupported_claim"
    assert update["retry_count"] == 1
```

## 15.3 必测异常场景

- LLM 返回非 JSON、字段缺失、类型错误、空计划或循环依赖。
- 向量库超时、数据库连接失败、HTTP 429/500、搜索无结果、沙箱超时。
- Retriever 返回跨租户文档、无效文档版本、重复 Chunk 或无页码内容。
- Tool 调用成功但响应格式变化，或外部写操作超时后实际已成功。
- 用户在审批期间修改请求、拒绝审批或重复提交恢复命令。
- Checkpoint 恢复后节点重复执行，验证幂等和审计是否正确。
- 模型或 Prompt 升级后路由、Skill 选择和引用质量回退。



# 16. 安全、权限与合规

## 16.1 威胁模型

| 风险 | 典型攻击 | 主要控制 |
| --- | --- | --- |
| Prompt Injection | 文档或网页要求忽略系统规则并调用危险工具 | 指令/数据分离、Tool 白名单、Reviewer、内容标记 |
| 越权检索 | 通过问题获取其他租户或部门文档 | ACL 前置过滤、数据库 RLS、权限测试 |
| SQL 注入/危险 SQL | 模型生成 DDL/DML 或绕过 LIMIT | AST 校验、只读账户、白名单、超时 |
| SSRF | HTTP Tool 请求内网地址或云元数据 | 无通用 URL Tool、域名/IP 白名单、网络隔离 |
| 代码执行 | Python 读取宿主机、联网或无限运行 | 容器沙箱、资源限制、无密钥、默认断网 |
| 数据泄露 | 密钥、PII、连接串进入 Trace 或回答 | 日志脱敏、Secret 管理、PII Middleware |
| 供应链风险 | 恶意依赖、Skill 脚本或解析器 | 锁版本、扫描、签名、发布审批、最小镜像 |
| 重复副作用 | 恢复/重试导致重复发送或更新 | 幂等键、事务、状态确认和审计 |

## 16.2 Prompt Injection 防护

- 将检索文档和网页内容明确标记为“不可信数据”，不得覆盖系统、Agent、Skill 和安全策略。
- 模型不能仅依据文档中的文字扩展工具权限；Tool 权限由服务端代码决定。
- 对要求读取密钥、系统 Prompt、内部路径、其他用户数据等内容直接拒绝或降级处理。
- 高风险场景让 Reviewer 检查工具调用理由、参数、数据范围和证据来源。
- 对新数据源和 Skill 执行红队评估，测试间接注入和多跳注入。

## 16.3 日志与隐私

- 使用结构化日志，默认不记录完整用户问题、完整文档片段、API Token 和数据库明文结果。
- 用户 ID 可 Hash；敏感 Trace 使用采样、脱敏、短保留或自托管策略。
- 对象存储工件使用租户隔离、短期签名 URL、服务端加密和生命周期规则。
- 明确数据保留、删除、导出、审计和模型供应商数据处理策略。



# 17. 部署、运维与成本控制

## 17.1 服务拆分

| 服务 | 建议职责 |
| --- | --- |
| api | 认证、会话 API、流式输出、审批接口、轻量 Graph 调用 |
| worker-ingestion | 文档解析、OCR、切分、Embedding、索引和增量同步 |
| worker-evaluation | 离线实验、批量在线评估、失败 Trace 处理 |
| sandbox | 隔离 Python 执行和文件生成 |
| postgres | 业务、Checkpoint、Store、文档、向量和审计；按规模拆分 |
| redis | 缓存、限流、锁和任务状态 |
| object-storage | 文档和工件 |

## 17.2 发布策略

1. 依赖、模型、Prompt、Skill、Retriever 和索引配置均生成独立版本标识。
2. 在 staging 运行黄金数据集和安全回归，指标达到门槛后再灰度。
3. 灰度期间按 release 标签对比质量、延迟、成本和错误率。
4. 出现回退时能够同时回滚代码、Prompt/Skill 版本和模型配置。
5. 索引结构重大变更使用双写/双索引，验证后切换别名，避免停机重建。

## 17.3 监控与告警

| 类别 | 关键指标 |
| --- | --- |
| 系统 | CPU、内存、连接池、队列长度、错误率、P95/P99 延迟 |
| 模型 | 调用成功率、429、超时、Token、成本、Fallback 比例 |
| Graph | 节点耗时、循环次数、最大步骤、Interrupt 等待时长 |
| RAG | 检索空结果率、Rerank 延迟、引用缺失率、索引新鲜度 |
| Tools | 调用成功率、重试、熔断、幂等冲突和外部依赖 SLA |
| 质量 | 在线 evaluator 分数、用户差评、Reviewer 拒绝率 |
| 安全 | 越权拒绝、危险 Tool 阻断、敏感信息检测和异常下载 |

## 17.4 成本优化

- 简单路由和校验使用更小模型，复杂规划和综合使用更强模型；通过模型配置档而不是散落代码选择。
- 缓存 Embedding、文档解析、查询改写和确定性 Tool 结果，但缓存键必须包含租户、权限和版本。
- 限制候选 Skill、Tool 描述、检索上下文和历史消息长度，避免上下文膨胀。
- 并行执行只用于真正独立步骤；并行并不总是更快，可能放大限流和成本。
- 在线评估采用采样和过滤，失败或高风险请求提高采样率。



# 18. 开发规范与常见问题

## 18.1 代码规范

- 启用 Ruff、Mypy/Pyright、Pytest；所有公共函数和结构模型具有类型标注。
- 异步调用链保持一致，避免在 async 节点中直接运行阻塞数据库、文件解析或 HTTP 代码。
- 配置通过 pydantic-settings 集中管理；模块导入时不创建外部连接或读取不必要 Secret。
- Prompt、Skill、SQL 模板和策略文件纳入 Git 评审，不在生产环境手工修改而无版本记录。
- 错误使用稳定 code 分类，用户消息与内部诊断分离。

## 18.2 常见反模式

| 反模式 | 后果 | 修正 |
| --- | --- | --- |
| 一个 Agent 绑定全部 Tools | 选择混乱、越权面扩大、难测试 | 专用 Agent + Skill + Tool 白名单 |
| 所有内容塞入 messages | Checkpoint 和上下文膨胀 | 结构化 State + artifact_id |
| 用自然语言解析计划 | 格式漂移、边界难验证 | Pydantic 结构化输出 |
| 只使用向量检索 | 编号和精确条款召回差 | Hybrid Search + Reranker |
| 检索后再做权限过滤 | 可能向模型泄露无权内容 | ACL 在查询层前置执行 |
| 无限 Reviewer 返工 | 死循环、成本不可控 | 有限 retry + 明确终止状态 |
| 任意 URL HTTP Tool | SSRF 和数据外传 | 业务 API 封装 + 网络白名单 |
| 主进程执行模型代码 | 远程代码执行和资源耗尽 | 独立沙箱 |
| 升级依赖不跑评估 | 路由和输出静默回退 | 锁版本 + 离线回归 + 灰度 |

## 18.3 典型故障排查

| 现象 | 优先检查 |
| --- | --- |
| Agent 总选错 Skill | Skill description 是否重叠、候选是否过多、选择数据集是否覆盖反例 |
| 回答有引用但不支持结论 | citation builder、Reviewer rubric、Chunk 边界和 Reranker |
| 长对话越来越慢 | Checkpoint 增长、消息压缩、Tool 大结果、历史引用是否未裁剪 |
| 恢复后重复发送/更新 | Interrupt 前副作用、幂等键、事务状态和重试策略 |
| 数据库查询慢或返回过多 | SQL LIMIT、索引、Schema 摘要、查询超时和结果工件化 |
| LangSmith Trace 泄露敏感信息 | 回调输入、metadata、Tool 返回、日志脱敏和采样策略 |
| 文档更新后仍引用旧内容 | 版本过滤、删除传播、索引别名、缓存键和有效期 |



# 19. 实施路线与验收清单

## 19.1 分阶段实施

| 阶段 | 范围 | 验收重点 |
| --- | --- | --- |
| MVP | 单知识库 RAG、多轮、引用、基础 Trace | 正确检索、权限隔离、可复现回答 |
| 多 Agent | Supervisor/Planner/Executor/Reviewer/Summary | 结构化计划、有限循环、错误分支 |
| Skills | Skill Registry、首批 Skills、选择与版本 | 激活准确率、按需加载、Tool 权限交集 |
| Tools | 数据库、HTTP、搜索、Python Sandbox | 最小权限、超时、审计、幂等和审批 |
| 质量工程 | 离线/在线评估、反馈、Dashboard | 回归门禁、告警、失败闭环 |
| 生产强化 | 高可用、压测、灾备、安全和成本 | SLO、故障恢复、渗透和容量基线 |

## 19.2 上线前架构清单

- □ 所有 LLM 决策输出均有 Schema 校验和错误处理。
- □ Graph 设置最大步骤、最大重试、总超时和明确终止路径。
- □ 生产使用持久化 Checkpointer，thread_id 和保留策略已验证。
- □ 知识库 ACL 在检索阶段生效，跨租户测试通过。
- □ 数据库默认只读；写操作、API 变更和发送行为有审批与幂等。
- □ HTTP 不支持任意 URL；Python 运行在独立沙箱且默认断网。
- □ Skill、Prompt、模型、索引和代码均可追踪到版本。
- □ LangSmith Trace 已脱敏，dev/staging/prod Project 分离。
- □ 黄金数据集、安全数据集和失败 Trace 回归已运行。
- □ 日志、指标、告警、备份、恢复和回滚流程已演练。

## 19.3 Definition of Done

- 功能：目标用例可完成，边界场景有明确失败或降级结果。
- 质量：离线评估不低于基线，关键安全指标必须全部通过。
- 可观测：Trace 能定位 Agent、Skill、Tool、文档引用和版本。
- 性能：达到约定 P95、并发、超时和成本指标。
- 安全：通过权限、注入、SQL、SSRF、沙箱和敏感数据测试。
- 运维：具备部署、回滚、告警、备份和故障处理文档。



# 官方参考资料

以下链接为本文档架构原则的主要官方依据。实施时应以当前官方文档和锁定依赖版本为准。

[1] LangGraph Overview：https://docs.langchain.com/oss/python/langgraph/overview

[2] LangGraph Application Structure：https://docs.langchain.com/oss/python/langgraph/application-structure

[3] LangGraph Persistence：https://docs.langchain.com/oss/python/langgraph/persistence

[4] LangGraph Subgraphs：https://docs.langchain.com/oss/python/langgraph/use-subgraphs

[5] LangGraph Interrupts：https://docs.langchain.com/oss/python/langgraph/interrupts

[6] LangGraph Testing：https://docs.langchain.com/oss/python/langgraph/test

[7] LangChain Retrieval：https://docs.langchain.com/oss/python/langchain/retrieval

[8] LangChain Tools：https://docs.langchain.com/oss/python/langchain/tools

[9] LangChain Middleware：https://docs.langchain.com/oss/python/langchain/middleware/overview

[10] Deep Agents Skills：https://docs.langchain.com/oss/python/deepagents/skills

[11] LangSmith Observability：https://docs.langchain.com/langsmith/observability

[12] LangSmith Evaluation：https://docs.langchain.com/langsmith/evaluation



# 附录 A. Agent—Skill—Tool 映射

| Agent | Skills | 允许 Tools（示例） |
| --- | --- | --- |
| Supervisor | intent-routing、risk-classification | 无业务写 Tool；仅上下文和策略查询 |
| Planner | task-planning、dependency-analysis | 无外部副作用 Tool |
| RAG Agent | document-question-answering、document-comparison | rewrite_query、knowledge_search、rerank_documents、build_citations |
| Database Agent | database-analysis | inspect_schema、execute_readonly_query |
| HTTP Agent | external-api-query | get_customer、get_order_status、create_ticket(需审批) |
| Search Agent | web-research、source-verification | web_search、read_page、rank_sources |
| Python Agent | python-data-analysis | inspect_artifact、execute_sandboxed_python |
| Reviewer | result-review、citation-review | 只读验证 Tool，不执行业务写操作 |
| Summarizer | final-summary | 无新事实检索，仅读取已审核工件 |



# 附录 B. 发布记录建议

**release-manifest.yaml**

```yaml
release_id: 2026.07.15.1
code_commit: <git_sha>
python_lock_hash: <sha256>
models:
  router: <provider/model/version>
  reasoning: <provider/model/version>
  embedding: <provider/model/version>
prompts:
  supervisor: 1.2.0
  reviewer: 1.1.0
skills:
  document-question-answering: 1.0.0
  database-analysis: 1.0.0
retrieval:
  splitter: semantic-v2
  vector_top_k: 20
  rerank_top_n: 6
index_version: kb-index-2026-07-15
baseline_experiment: <langsmith_experiment_id>
```



# 附录 C. 最小 MVP 范围

为避免首期范围过大，建议 MVP 只实现以下闭环：

- FastAPI 对话接口与 SSE 流式输出。
- 一个 PostgreSQL/pgvector 知识库，支持 PDF/DOCX/Markdown 入库。
- RAG Agent：问题改写、混合检索、Rerank、引用回答。
- LangGraph State、PostgreSQL Checkpointer 和基本错误处理。
- 三个 Skills：document-question-answering、result-review、final-summary。
- 两个 Tools：knowledge_search、rerank_documents。
- LangSmith Trace 与一套 30～100 条黄金评估数据。
- 基础租户/知识库权限和引用定位。

> 范围控制｜MVP 暂缓项：数据库写操作、任意复杂 API 自动化、开放网络 Python、动态 Skill 平台和大规模多 Agent 并行，建议在基础 RAG 质量和安全边界稳定后逐步加入。






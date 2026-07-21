"""Application service for executing a single agent run."""

from dataclasses import dataclass
from typing import Any, cast

from agent.modules.agent_runtime.graphs.main_graph.state import AgentRunState


@dataclass(frozen=True, slots=True)
class RunResult:
    run_id: str
    final_answer: str
    evidence_count: int


class RunService:
    """Execute a compiled graph without coupling the application layer to LangGraph types."""

    def __init__(self, graph: Any) -> None:
        self._graph = graph

    async def execute(self, *, run_id: str, query: str) -> RunResult:
        result = cast(
            AgentRunState,
            await self._graph.ainvoke({"run_id": run_id, "query": query}),
        )
        evidence = result.get("evidence", [])
        return RunResult(
            run_id=run_id,
            final_answer=result["final_answer"],
            evidence_count=len(evidence),
        )

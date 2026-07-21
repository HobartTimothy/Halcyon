"""Agent runtime tasks."""

import asyncio

from agent.entrypoints.workers.celery_app import celery_app
from agent.modules.agent_runtime.application.run_service import RunService
from agent.modules.agent_runtime.graphs.main_graph.builder import build_main_graph


@celery_app.task(name="agent.run.execute")  # type: ignore[untyped-decorator]
def execute_run(run_id: str, query: str) -> dict[str, object]:
    """Execute the demo graph in a worker process."""

    service = RunService(build_main_graph())
    result = asyncio.run(service.execute(run_id=run_id, query=query))
    return {
        "run_id": result.run_id,
        "final_answer": result.final_answer,
        "evidence_count": result.evidence_count,
    }

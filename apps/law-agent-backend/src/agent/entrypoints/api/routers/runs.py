"""Agent run HTTP endpoints."""

from uuid import uuid4

from fastapi import APIRouter, Request

from agent.entrypoints.api.schemas.runs import DemoRunRequest, DemoRunResponse
from agent.modules.agent_runtime.application.run_service import RunService

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])


@router.post("/demo", response_model=DemoRunResponse)
async def execute_demo_run(payload: DemoRunRequest, request: Request) -> DemoRunResponse:
    service: RunService = request.app.state.run_service
    result = await service.execute(run_id=str(uuid4()), query=payload.query)
    return DemoRunResponse(
        run_id=result.run_id,
        final_answer=result.final_answer,
        evidence_count=result.evidence_count,
    )

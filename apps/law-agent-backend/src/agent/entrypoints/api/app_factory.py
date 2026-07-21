"""FastAPI application factory."""

from fastapi import FastAPI

from agent.entrypoints.api.routers.health import router as health_router
from agent.entrypoints.api.routers.runs import router as runs_router
from agent.modules.agent_runtime.application.run_service import RunService
from agent.modules.agent_runtime.graphs.main_graph.builder import build_main_graph


def create_app() -> FastAPI:
    app = FastAPI(title="Enterprise AI Agent", version="0.1.0")
    app.state.run_service = RunService(build_main_graph())
    app.include_router(health_router)
    app.include_router(runs_router)
    return app

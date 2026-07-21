"""SSE application factory.

The foundation endpoint emits a persisted-state snapshot. A later phase replaces
this generator with a Valkey Streams reader supporting Last-Event-ID recovery.
"""

import json
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from agent.shared.contracts.run_events import RunEvent


async def _snapshot_stream(run_id: str) -> AsyncIterator[str]:
    event = RunEvent(
        event_id="0-0",
        event_type="stream.snapshot",
        run_id=run_id,
        sequence=0,
        data={"status": "foundation-skeleton"},
    )
    payload = json.dumps(event.model_dump(), ensure_ascii=False, separators=(",", ":"))
    yield f"id: {event.event_id}\nevent: {event.event_type}\ndata: {payload}\n\n"


def create_stream_app() -> FastAPI:
    app = FastAPI(title="Enterprise AI Agent Stream API", version="0.1.0")

    @app.get("/health/live")
    async def liveness() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/runs/{run_id}/events", response_class=StreamingResponse)
    async def run_events(run_id: str) -> StreamingResponse:
        return StreamingResponse(
            _snapshot_stream(run_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "X-Accel-Buffering": "no",
            },
        )

    return app

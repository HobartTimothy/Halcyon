from fastapi.testclient import TestClient

from agent.entrypoints.stream_api.app_factory import create_stream_app


def test_demo_stream_uses_event_stream_content_type() -> None:
    client = TestClient(create_stream_app())
    response = client.get("/api/v1/runs/run-1/events")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: stream.snapshot" in response.text

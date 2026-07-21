from fastapi.testclient import TestClient

from agent.entrypoints.api.app_factory import create_app


def test_liveness() -> None:
    client = TestClient(create_app())
    assert client.get("/health/live").json() == {"status": "ok"}

from fastapi.testclient import TestClient

from agent.entrypoints.api.app_factory import create_app


def test_demo_run_executes_graph() -> None:
    client = TestClient(create_app())
    response = client.post("/api/v1/runs/demo", json={"query": "leave policy"})

    assert response.status_code == 200
    body = response.json()
    assert body["evidence_count"] == 3
    assert body["final_answer"] == "Collected 3 evidence items for: leave policy"

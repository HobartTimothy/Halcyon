import pytest

from agent.modules.agent_runtime.graphs.main_graph.builder import build_main_graph


@pytest.mark.asyncio
async def test_main_graph_fans_out_and_joins_evidence() -> None:
    graph = build_main_graph()
    result = await graph.ainvoke({"run_id": "run-1", "query": "leave policy"})

    assert [item.evidence_id for item in result["evidence"]] == [
        "memory:run-1",
        "rag:run-1",
        "web:run-1",
    ]
    assert result["final_answer"] == "Collected 3 evidence items for: leave policy"

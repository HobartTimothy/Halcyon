from agent.modules.agent_runtime.domain.evidence import EvidenceItem
from agent.modules.agent_runtime.graphs.main_graph.reducers import merge_evidence


def make_item(evidence_id: str, score: float, excerpt: str = "content") -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        source_type="knowledge_chunk",
        title="Policy",
        excerpt=excerpt,
        relevance_score=score,
    )


def test_merge_evidence_is_idempotent() -> None:
    item = make_item("rag:1", 0.8)
    assert merge_evidence([item], [item]) == [item]


def test_merge_evidence_keeps_higher_relevance_version() -> None:
    low = make_item("rag:1", 0.4, "short")
    high = make_item("rag:1", 0.9, "more complete")
    assert merge_evidence([low], [high]) == [high]


def test_merge_evidence_has_stable_order() -> None:
    first = make_item("web:2", 0.7)
    second = make_item("memory:1", 0.6)
    assert [item.evidence_id for item in merge_evidence([first], [second])] == [
        "memory:1",
        "web:2",
    ]

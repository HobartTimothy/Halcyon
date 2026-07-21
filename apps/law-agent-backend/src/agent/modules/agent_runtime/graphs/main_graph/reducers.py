"""Deterministic reducers for parallel graph channels."""

from agent.modules.agent_runtime.domain.evidence import EvidenceItem


def merge_evidence(
    left: list[EvidenceItem] | None,
    right: list[EvidenceItem] | None,
) -> list[EvidenceItem]:
    """Merge evidence by ID, retaining the highest-relevance representation."""

    merged = {item.evidence_id: item for item in (left or [])}
    for item in right or []:
        current = merged.get(item.evidence_id)
        if current is None or item.relevance_score > current.relevance_score:
            merged[item.evidence_id] = item
    return [merged[key] for key in sorted(merged)]

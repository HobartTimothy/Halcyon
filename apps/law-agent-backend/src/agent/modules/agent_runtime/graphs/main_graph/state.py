from typing import Annotated, TypedDict

from agent.modules.agent_runtime.domain.evidence import EvidenceItem
from agent.modules.agent_runtime.graphs.main_graph.reducers import merge_evidence


class AgentRunState(TypedDict, total=False):

    run_id: str
    query: str
    evidence: Annotated[list[EvidenceItem], merge_evidence]
    final_answer: str

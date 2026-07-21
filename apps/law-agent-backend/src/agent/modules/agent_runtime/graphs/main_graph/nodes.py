"""Deterministic node implementations used by the foundation skeleton."""

from agent.modules.agent_runtime.domain.evidence import EvidenceItem
from agent.modules.agent_runtime.graphs.main_graph.state import AgentRunState


def rag_agent(state: AgentRunState) -> AgentRunState:
    return {
        "evidence": [
            EvidenceItem(
                evidence_id=f"rag:{state['run_id']}",
                source_type="knowledge_chunk",
                title="Internal knowledge",
                excerpt=f"RAG evidence for {state['query']}",
                relevance_score=0.90,
            )
        ]
    }


def web_agent(state: AgentRunState) -> AgentRunState:
    return {
        "evidence": [
            EvidenceItem(
                evidence_id=f"web:{state['run_id']}",
                source_type="web_page",
                title="External source",
                excerpt=f"Web evidence for {state['query']}",
                relevance_score=0.80,
            )
        ]
    }


def memory_agent(state: AgentRunState) -> AgentRunState:
    return {
        "evidence": [
            EvidenceItem(
                evidence_id=f"memory:{state['run_id']}",
                source_type="user_memory",
                title="User memory",
                excerpt=f"Memory evidence for {state['query']}",
                relevance_score=0.70,
            )
        ]
    }


def compose_answer(state: AgentRunState) -> AgentRunState:
    evidence = state.get("evidence", [])
    return {"final_answer": f"Collected {len(evidence)} evidence items for: {state['query']}"}

"""Factory for the versioned main LangGraph."""

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent.modules.agent_runtime.graphs.main_graph.nodes import (
    compose_answer,
    memory_agent,
    rag_agent,
    web_agent,
)
from agent.modules.agent_runtime.graphs.main_graph.state import AgentRunState


def build_main_graph() -> CompiledStateGraph[AgentRunState, None, AgentRunState, AgentRunState]:
    """Compile a deterministic parallel research graph.

    Real providers will replace the deterministic research nodes in later phases.
    """

    builder = StateGraph(AgentRunState)
    builder.add_node("rag_agent", rag_agent)
    builder.add_node("web_agent", web_agent)
    builder.add_node("memory_agent", memory_agent)
    builder.add_node("compose_answer", compose_answer)

    builder.add_edge(START, "rag_agent")
    builder.add_edge(START, "web_agent")
    builder.add_edge(START, "memory_agent")
    builder.add_edge("rag_agent", "compose_answer")
    builder.add_edge("web_agent", "compose_answer")
    builder.add_edge("memory_agent", "compose_answer")
    builder.add_edge("compose_answer", END)
    return builder.compile()

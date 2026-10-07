from agent.modules.skills.skill_runtime import get_default_skill_runtime


def test_legal_research_skill_renders_for_search_agent() -> None:
    runtime = get_default_skill_runtime()
    prompt = runtime.render_for_agent("legal_search_agent")

    assert "legal-research" in prompt
    assert len(prompt) >= 100

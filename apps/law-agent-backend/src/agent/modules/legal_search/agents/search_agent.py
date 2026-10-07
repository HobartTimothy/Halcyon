from langchain.agents import create_agent

from agent.modules.llm.factory import get_chat_model
from agent.modules.legal_search.prompts.prompts import build_search_system_prompt
from agent.modules.skills.skill_runtime import get_default_skill_runtime
from agent.modules.tools.search.page_reader import read_legal_page
from agent.modules.tools.search.web_search import (
    search_authoritative_legal_sources,
    search_jurisdiction_legal_sources,
    search_official_legal_sources,
    search_supplementary_web,
)


AGENT_NAME = "legal_search_agent"


def search_agent():
    # 获取模型
    model = get_chat_model()

    # 获取skill
    skill_prompt = get_default_skill_runtime().render_for_agent(AGENT_NAME)

    # 构建系统提示
    system_prompt = build_search_system_prompt(skill_prompt)

    # 创建代理对象
    return create_agent(
        model=model,
        system_prompt=system_prompt,
        name=AGENT_NAME,
        tools=[
            search_official_legal_sources,
            search_authoritative_legal_sources,
            search_jurisdiction_legal_sources,
            search_supplementary_web,
            read_legal_page,
        ],
    )
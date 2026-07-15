from langchain.agents import create_agent

from lows_agent.llm.factory import get_chat_model
from lows_agent.tools.search.page_reader import read_legal_page
from lows_agent.prompts.search.prompts import build_search_system_prompt
from lows_agent.tools.search.web_search import search_authoritative_legal_sources, search_jurisdiction_legal_sources,search_official_legal_sources, search_supplementary_web



def search_agent():
    
    model = get_chat_model()

    system_prompt = build_search_system_prompt(load_legal_research_skill())
    return create_agent(
        model=model,
        tools=[
            search_official_legal_sources,
            search_authoritative_legal_sources,
            search_jurisdiction_legal_sources,
            search_supplementary_web,
            read_legal_page,
        ],
        system_prompt=system_prompt,
        name="legal_search_agent",
    )

from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain.tools import tool
from langchain_tavily import TavilySearch

from .source_ranker import rank_search_results


PREFERRED_LEGAL_DOMAINS = (
    "flk.npc.gov.cn",
    "www.moj.gov.cn",
    "alk.12348.gov.cn",
)

AUTHORITATIVE_LEGAL_DOMAINS = (
    "gov.cn",
    "npc.gov.cn",
    "court.gov.cn",
    "spp.gov.cn",
    "12348.gov.cn",
)

JURISDICTION_DOMAINS = {
    "china": (
        "flk.npc.gov.cn",
        "npc.gov.cn",
        "gov.cn",
        "moj.gov.cn",
        "court.gov.cn",
        "spp.gov.cn",
        "alk.12348.gov.cn",
    ),
    "united_states": (
        "congress.gov",
        "uscode.house.gov",
        "govinfo.gov",
        "ecfr.gov",
        "supremecourt.gov",
        "uscourts.gov",
        "justice.gov",
    ),
    "european_union": (
        "eur-lex.europa.eu",
        "curia.europa.eu",
    ),
    "united_kingdom": (
        "legislation.gov.uk",
        "supremecourt.uk",
        "judiciary.uk",
    ),
}

_JURISDICTION_ALIASES = {
    "china": "china",
    "cn": "china",
    "prc": "china",
    "中国": "china",
    "中国大陆": "china",
    "united_states": "united_states",
    "united states": "united_states",
    "us": "united_states",
    "usa": "united_states",
    "美国": "united_states",
    "european_union": "european_union",
    "european union": "european_union",
    "eu": "european_union",
    "欧盟": "european_union",
    "united_kingdom": "united_kingdom",
    "united kingdom": "united_kingdom",
    "uk": "united_kingdom",
    "英国": "united_kingdom",
}

MAX_QUERY_LENGTH = 500
MAX_RAW_CONTENT_CHARS = 6000


@lru_cache(maxsize=1)
def _get_tavily_search() -> TavilySearch:
    return TavilySearch(
        max_results=8,
        topic="general",
        search_depth="advanced",
        include_answer=False,
        include_raw_content=True,
        include_images=False,
    )


def _validate_query(query: str) -> str:
    cleaned = " ".join(query.split())
    if not cleaned:
        raise ValueError("query must not be empty")
    if len(cleaned) > MAX_QUERY_LENGTH:
        raise ValueError(f"query must not exceed {MAX_QUERY_LENGTH} characters")
    return cleaned


def normalize_jurisdiction(jurisdiction: str) -> str:
    try:
        key = " ".join(jurisdiction.strip().lower().replace("-", " ").split())
    except (AttributeError, TypeError) as exc:
        raise ValueError("jurisdiction must be text") from exc
    normalized = _JURISDICTION_ALIASES.get(key)
    if normalized is None:
        raise ValueError(f"unsupported jurisdiction: {jurisdiction}")
    return normalized


def _normalize_provider_results(
    provider_response: dict[str, Any],
    *,
    source_scope: str,
) -> list[dict[str, Any]]:
    normalized = []
    for item in provider_response.get("results", []):
        url = item.get("url")
        if not url:
            continue
        raw_content = item.get("raw_content")
        normalized.append(
            {
                "title": item.get("title"),
                "url": url,
                "summary": item.get("content"),
                "raw_content": (
                    raw_content[:MAX_RAW_CONTENT_CHARS] if raw_content else None
                ),
                "score": item.get("score"),
                "source_scope": source_scope,
            }
        )
    return rank_search_results(normalized, limit=8)


def _search(
    query: str,
    *,
    source_scope: str,
    include_domains: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    try:
        cleaned_query = _validate_query(query)
    except (AttributeError, TypeError, ValueError) as exc:
        return {
            "ok": False,
            "query": str(query),
            "source_scope": source_scope,
            "results": [],
            "error": "invalid_query",
            "message": str(exc),
        }

    payload: dict[str, Any] = {"query": cleaned_query}
    if include_domains:
        payload["include_domains"] = list(include_domains)

    try:
        response = _get_tavily_search().invoke(payload)
        if not isinstance(response, dict):
            raise TypeError("unexpected Tavily response")
    except Exception as exc:
        return {
            "ok": False,
            "query": cleaned_query,
            "source_scope": source_scope,
            "results": [],
            "error": "search_provider_error",
            "error_type": type(exc).__name__,
        }

    return {
        "ok": True,
        "query": cleaned_query,
        "source_scope": source_scope,
        "results": _normalize_provider_results(
            response,
            source_scope=source_scope,
        ),
    }


@tool
def search_official_legal_sources(query: str) -> dict[str, Any]:
    """搜索首选官方法律来源。

    限定国家法律法规数据库、司法部官网和司法行政（法律服务）案例库。
    涉及中国法律问题时应首先调用本工具。
    """
    return _search(
        query,
        source_scope="preferred_official_legal_sources",
        include_domains=PREFERRED_LEGAL_DOMAINS,
    )


@tool
def search_authoritative_legal_sources(query: str) -> dict[str, Any]:
    """搜索政府、人大、法院、检察院等权威法律来源。

    仅在首选三个来源结果不足或需要交叉验证时调用。
    """
    return _search(
        query,
        source_scope="authoritative_legal_sources",
        include_domains=AUTHORITATIVE_LEGAL_DOMAINS,
    )


@tool
def search_jurisdiction_legal_sources(
    query: str,
    jurisdiction: str,
) -> dict[str, Any]:
    """按指定法域搜索第一手官方法律来源。

    支持中国、美国、欧盟和英国。调用前应先根据用户问题确定法域；
    州、省、成员国等更细层级仍需在查询词中明确。
    """
    try:
        normalized = normalize_jurisdiction(jurisdiction)
    except ValueError as exc:
        return {
            "ok": False,
            "query": query,
            "jurisdiction": str(jurisdiction),
            "source_scope": "jurisdiction_official_sources",
            "results": [],
            "error": "unsupported_jurisdiction",
            "message": str(exc),
            "supported_jurisdictions": list(JURISDICTION_DOMAINS),
        }

    response = _search(
        query,
        source_scope=f"jurisdiction_official_sources:{normalized}",
        include_domains=JURISDICTION_DOMAINS[normalized],
    )
    response["jurisdiction"] = normalized
    return response


@tool
def search_supplementary_web(query: str) -> dict[str, Any]:
    """搜索普通互联网补充资料。

    仅在官方和权威来源仍不足时调用；结果不得替代现行官方法律原文。
    """
    return _search(query, source_scope="supplementary_web")

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


_TRACKING_QUERY_KEYS = {
    "from",
    "source",
    "spm",
    "ref",
    "referrer",
}


def _domain_matches(host: str, domain: str) -> bool:
    return host == domain or host.endswith(f".{domain}")


def assess_source(url: str) -> dict[str, Any]:
    """Classify a URL by legal authority without claiming document validity."""
    host = (urlsplit(url).hostname or "").lower().rstrip(".")

    if _domain_matches(host, "flk.npc.gov.cn"):
        return {
            "host": host,
            "name": "国家法律法规数据库",
            "source_type": "legislation_database",
            "citation_role": "primary_law_source",
            "authority_score": 100,
        }
    if _domain_matches(host, "moj.gov.cn"):
        return {
            "host": host,
            "name": "中华人民共和国司法部",
            "source_type": "judicial_administration",
            "citation_role": "official_admin_source",
            "authority_score": 94,
        }
    if _domain_matches(host, "alk.12348.gov.cn"):
        return {
            "host": host,
            "name": "司法行政（法律服务）案例库",
            "source_type": "legal_service_case_library",
            "citation_role": "case_reference_only",
            "authority_score": 86,
        }
    if _domain_matches(host, "npc.gov.cn"):
        return {
            "host": host,
            "name": "全国人民代表大会",
            "source_type": "legislature",
            "citation_role": "primary_law_source",
            "authority_score": 98,
        }
    if _domain_matches(host, "court.gov.cn"):
        return {
            "host": host,
            "name": "人民法院网站",
            "source_type": "court",
            "citation_role": "official_judicial_source",
            "authority_score": 91,
        }
    if _domain_matches(host, "spp.gov.cn"):
        return {
            "host": host,
            "name": "人民检察院网站",
            "source_type": "procuratorate",
            "citation_role": "official_judicial_source",
            "authority_score": 91,
        }
    if _domain_matches(host, "gov.cn"):
        return {
            "host": host,
            "name": "中国政府网或政府网站",
            "source_type": "government",
            "citation_role": "official_government_source",
            "authority_score": 92,
        }
    if host.endswith(".gov.cn"):
        return {
            "host": host,
            "name": "其他政府网站",
            "source_type": "government",
            "citation_role": "official_government_source",
            "authority_score": 82,
        }
    if _domain_matches(host, "chinacourt.org"):
        return {
            "host": host,
            "name": "中国法院网",
            "source_type": "judicial_media",
            "citation_role": "official_judicial_reference",
            "authority_score": 78,
        }

    return {
        "host": host,
        "name": host or "未知来源",
        "source_type": "secondary_web",
        "citation_role": "secondary_reference",
        "authority_score": 30,
    }


def canonicalize_url(url: str) -> str:
    """Remove fragments and tracking parameters while retaining document IDs."""
    parts = urlsplit(url.strip())
    filtered_query = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        lowered = key.lower()
        if lowered.startswith("utm_") or lowered in _TRACKING_QUERY_KEYS:
            continue
        filtered_query.append((key, value))

    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path or "/",
            urlencode(filtered_query, doseq=True),
            "",
        )
    )


def _ranking_score(result: Mapping[str, Any], source: Mapping[str, Any]) -> float:
    try:
        relevance = float(result.get("score") or 0.0)
    except (TypeError, ValueError):
        relevance = 0.0
    relevance = max(0.0, min(1.0, relevance))
    authority = float(source["authority_score"]) / 100.0
    content_bonus = 0.05 if result.get("raw_content") or result.get("summary") else 0.0
    return round(authority * 0.60 + relevance * 0.35 + content_bonus, 4)


def rank_search_results(
    results: Iterable[Mapping[str, Any]],
    *,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Deduplicate, annotate and rank search results without mutating inputs."""
    best_by_url: dict[str, dict[str, Any]] = {}

    for original in results:
        url = str(original.get("url") or "").strip()
        if not url:
            continue
        canonical_url = canonicalize_url(url)
        source = assess_source(canonical_url)
        enriched = dict(original)
        enriched["url"] = canonical_url
        enriched["source"] = source
        enriched["rank_score"] = _ranking_score(enriched, source)

        existing = best_by_url.get(canonical_url)
        if existing is None or enriched["rank_score"] > existing["rank_score"]:
            best_by_url[canonical_url] = enriched

    ranked = sorted(
        best_by_url.values(),
        key=lambda item: (item["rank_score"], item["source"]["authority_score"]),
        reverse=True,
    )
    return ranked[:limit] if limit is not None else ranked
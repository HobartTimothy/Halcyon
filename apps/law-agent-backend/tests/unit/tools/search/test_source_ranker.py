from agent.modules.tools.search.source_ranker import assess_source


def test_us_federal_primary_law_source() -> None:
    source = assess_source("https://www.congress.gov/bill/118th-congress")

    assert source["source_type"] == "us_federal_primary_law"
    assert source["authority_score"] >= 95


def test_eu_primary_law_source() -> None:
    source = assess_source("https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX")

    assert source["source_type"] == "eu_primary_law"
    assert source["authority_score"] >= 95

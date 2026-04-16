from __future__ import annotations

import argparse
from urllib.parse import quote_plus

from common import LiteratureRecord, add_output_argument, default_output_path, http_session, print_json, write_json


def infer_relevance(query: str, title: str, abstract: str, year: int | None) -> str:
    text = f"{title} {abstract}".lower()
    query_terms = [term.strip().lower() for term in query.split() if term.strip()]
    overlap = [term for term in query_terms if term in text]
    recency = ""
    if year and year >= 2021:
        recency = "较新文献；"
    if overlap:
        return f"{recency}与检索主题直接相关，命中关键词：{', '.join(overlap[:4])}。"
    return f"{recency}可作为相邻主题或方法启发文献。"


def normalize_year(raw: str | None) -> int | None:
    if not raw:
        return None
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) >= 4:
        return int(digits[:4])
    return None


def search_openalex(query: str, language: str, limit: int) -> list[LiteratureRecord]:
    session = http_session()
    params = {
        "search": query,
        "per-page": limit,
        "mailto": "literature-harvest@example.invalid",
    }
    response = session.get("https://api.openalex.org/works", params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    records: list[LiteratureRecord] = []
    for item in payload.get("results", []):
        title = item.get("title") or ""
        abstract = ""
        primary_location = item.get("primary_location") or {}
        source = primary_location.get("source") or {}
        inverted = item.get("abstract_inverted_index") or {}
        if inverted:
            ordered: list[tuple[int, str]] = []
            for word, positions in inverted.items():
                for pos in positions:
                    ordered.append((pos, word))
            abstract = " ".join(word for _, word in sorted(ordered))
        authors = [author.get("author", {}).get("display_name", "") for author in item.get("authorships", [])]
        record = LiteratureRecord(
            source="openalex",
            title=title,
            authors=[author for author in authors if author],
            year=item.get("publication_year"),
            journal=source.get("display_name", ""),
            abstract=abstract,
            keywords=[concept.get("display_name", "") for concept in item.get("concepts", [])[:8]],
            doi=(item.get("doi") or "").replace("https://doi.org/", ""),
            url=primary_location.get("landing_page_url", "") or item.get("id", ""),
            pdf_path="",
            language=language or "",
            access_status="metadata_only",
            relevance_note=infer_relevance(query, title, abstract, item.get("publication_year")),
        )
        records.append(record)
    return records


def search_crossref(query: str, language: str, limit: int) -> list[LiteratureRecord]:
    session = http_session()
    params = {"query": query, "rows": limit}
    response = session.get("https://api.crossref.org/works", params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    records: list[LiteratureRecord] = []
    for item in payload.get("message", {}).get("items", []):
        title = " ".join(item.get("title") or [])
        abstract = item.get("abstract") or ""
        authors = []
        for author in item.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            full = " ".join(part for part in [given, family] if part)
            if full:
                authors.append(full)
        journal = " ".join(item.get("container-title") or [])
        year = None
        parts = item.get("published-print", {}).get("date-parts") or item.get("published-online", {}).get("date-parts") or []
        if parts and parts[0]:
            year = parts[0][0]
        record = LiteratureRecord(
            source="crossref",
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            abstract=abstract,
            keywords=[],
            doi=item.get("DOI", ""),
            url=item.get("URL", ""),
            pdf_path="",
            language=language or "",
            access_status="metadata_only",
            relevance_note=infer_relevance(query, title, abstract, year),
        )
        records.append(record)
    return records


def search_semantic_scholar(query: str, language: str, limit: int) -> list[LiteratureRecord]:
    session = http_session()
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,year,authors,venue,externalIds,url",
    }
    response = session.get("https://api.semanticscholar.org/graph/v1/paper/search", params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    records: list[LiteratureRecord] = []
    for item in payload.get("data", []):
        title = item.get("title") or ""
        abstract = item.get("abstract") or ""
        year = item.get("year")
        doi = (item.get("externalIds") or {}).get("DOI", "")
        record = LiteratureRecord(
            source="semantic_scholar",
            title=title,
            authors=[author.get("name", "") for author in item.get("authors", []) if author.get("name")],
            year=year,
            journal=item.get("venue", ""),
            abstract=abstract,
            keywords=[],
            doi=doi,
            url=item.get("url", "") or (f"https://doi.org/{doi}" if doi else ""),
            pdf_path="",
            language=language or "",
            access_status="metadata_only",
            relevance_note=infer_relevance(query, title, abstract, year),
        )
        records.append(record)
    return records


def search_pubmed(query: str, language: str, limit: int) -> list[LiteratureRecord]:
    session = http_session()
    response = session.get(
        f"https://pubmed.ncbi.nlm.nih.gov/?term={quote_plus(query)}&size={limit}&format=pubmed",
        timeout=30,
    )
    response.raise_for_status()
    records: list[LiteratureRecord] = []
    blocks = [block.strip() for block in response.text.split("\n\n") if block.strip()]
    for block in blocks[:limit]:
        fields: dict[str, list[str]] = {}
        for line in block.splitlines():
            if "-" not in line:
                continue
            key, value = line.split("-", 1)
            fields.setdefault(key.strip(), []).append(value.strip())
        title = " ".join(fields.get("TI", []))
        abstract = " ".join(fields.get("AB", []))
        year = normalize_year(" ".join(fields.get("DP", [])))
        record = LiteratureRecord(
            source="pubmed",
            title=title,
            authors=fields.get("FAU", []),
            year=year,
            journal=" ".join(fields.get("JT", [])),
            abstract=abstract,
            keywords=fields.get("MH", []),
            doi="",
            url="",
            pdf_path="",
            language=language or "",
            access_status="metadata_only",
            relevance_note=infer_relevance(query, title, abstract, year),
        )
        records.append(record)
    return records


SOURCE_MAP = {
    "openalex": search_openalex,
    "crossref": search_crossref,
    "semantic_scholar": search_semantic_scholar,
    "pubmed": search_pubmed,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Search open metadata sources for literature candidates.")
    parser.add_argument("--query", required=True, help="Search query.")
    parser.add_argument("--language", default="", help="Language hint, typically zh or en.")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum results per source.")
    parser.add_argument(
        "--sources",
        nargs="+",
        default=["openalex", "crossref"],
        choices=sorted(SOURCE_MAP.keys()),
        help="Sources to query.",
    )
    add_output_argument(parser)
    args = parser.parse_args()

    records = []
    for source in args.sources:
        records.extend(record.to_dict() for record in SOURCE_MAP[source](args.query, args.language, args.max_results))

    output = {"query": args.query, "records": records}
    out_path = args.output or default_output_path("search-open", args.query)
    write_json(out_path, output)
    print_json({"output": str(out_path), "count": len(records), "records": records})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

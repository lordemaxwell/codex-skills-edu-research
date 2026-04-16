from __future__ import annotations

import argparse
import re
from pathlib import Path

from build_manifest import main as _unused  # keeps module discoverable for future edits
from common import RUNS_DIR, load_local_env, print_json, slugify, write_json
from fetch_cnki import run_fetch as run_cnki_fetch
from import_zotero import create_items, stage_manual_files
from search_open import SOURCE_MAP


def dedupe_records(records: list[dict]) -> list[dict]:
    seen: set[str] = set()
    deduped: list[dict] = []
    for record in records:
        doi = (record.get("doi") or "").strip().lower()
        title = (record.get("title") or "").strip().lower()
        key = doi or title
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


EN_STOPWORDS = {
    "the", "and", "for", "with", "from", "into", "based", "data", "study", "research",
    "analysis", "china", "household", "effect", "effects", "impact", "mechanism",
}


def english_terms(query: str) -> list[str]:
    tokens = re.split(r"[^a-z0-9]+", query.lower())
    return [token for token in tokens if len(token) >= 4 and token not in EN_STOPWORDS]


def chinese_terms(query: str) -> list[str]:
    return [token for token in re.split(r"[\s,，;；]+", query) if token]


def relevance_score(record: dict, terms: list[str]) -> int:
    text = f"{record.get('title', '')} {record.get('abstract', '')}".lower()
    score = 0
    for term in terms:
        lowered = term.lower()
        if lowered and lowered in text:
            score += 2 if lowered in (record.get("title", "") or "").lower() else 1
    return score


def filter_records(records: list[dict], en_query: str | None, zh_query: str | None) -> list[dict]:
    en_terms = english_terms(en_query or "")
    zh_terms = chinese_terms(zh_query or "")
    kept: list[dict] = []
    for record in records:
        language = (record.get("language") or "").lower()
        if language == "en":
            score = relevance_score(record, en_terms)
            if score >= 2:
                kept.append(record)
        elif language == "zh":
            score = relevance_score(record, zh_terms)
            if score >= 1:
                kept.append(record)
        else:
            kept.append(record)
    return kept


def main() -> int:
    load_local_env()
    parser = argparse.ArgumentParser(description="One-shot topic harvest: search, build manifest, create collection, and import to Zotero.")
    parser.add_argument("--query", required=True, help="Logical topic name for the overall run.")
    parser.add_argument("--collection", required=True, help="Target Zotero collection name.")
    parser.add_argument("--english-query", help="Query for English literature sources.")
    parser.add_argument("--chinese-query", help="Query for CNKI.")
    parser.add_argument("--open-results", type=int, default=6, help="Maximum results per open source.")
    parser.add_argument("--cnki-results", type=int, default=5, help="Maximum CNKI results.")
    parser.add_argument(
        "--open-sources",
        nargs="+",
        default=["openalex", "crossref", "semantic_scholar"],
        choices=sorted(SOURCE_MAP.keys()),
        help="Open metadata sources for English literature.",
    )
    parser.add_argument("--skip-open", action="store_true", help="Skip English-source harvesting.")
    parser.add_argument("--skip-cnki", action="store_true", help="Skip CNKI harvesting.")
    parser.add_argument("--show-browser", action="store_true", help="Show browser and allow manual login when harvesting CNKI.")
    args = parser.parse_args()

    all_records: list[dict] = []
    errors: list[dict] = []

    if not args.skip_open:
        open_query = args.english_query or args.query
        for source in args.open_sources:
            try:
                records = SOURCE_MAP[source](open_query, "en", args.open_results)
                all_records.extend(record.to_dict() for record in records)
            except Exception as exc:
                errors.append({"source": source, "query": open_query, "error": str(exc)})

    if not args.skip_cnki:
        cnki_query = args.chinese_query or args.query
        try:
            all_records.extend(
                run_cnki_fetch(
                    query=cnki_query,
                    max_results=args.cnki_results,
                    profile_dir=Path(__file__).resolve().parent.parent / "profiles" / "cnki",
                    show_browser=args.show_browser,
                    download_pdf=False,
                )
            )
        except Exception as exc:
            errors.append({"source": "cnki", "query": cnki_query, "error": str(exc)})

    records = dedupe_records(filter_records(all_records, args.english_query or args.query, args.chinese_query or args.query))
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = RUNS_DIR / f"manifest-{slugify(args.collection, 'manifest')}.json"
    manifest = {
        "query": args.query,
        "collection": args.collection,
        "count": len(records),
        "errors": errors,
        "records": records,
    }
    write_json(manifest_path, manifest)

    result = {
        "mode": "web_api",
        "manifest": str(manifest_path),
        "created": create_items(records, args.collection, args.query),
        "manual_files": stage_manual_files(records, args.collection),
        "count": len(records),
        "errors": errors,
    }
    print_json(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

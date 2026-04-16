from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

from common import MANUAL_DIR, http_session, load_local_env, print_json, read_json, slugify, write_json


def zotero_headers() -> dict[str, str]:
    api_key = os.environ.get("ZOTERO_API_KEY", "")
    return {"Zotero-API-Key": api_key, "Content-Type": "application/json"}


def zotero_base() -> str:
    user_id = os.environ.get("ZOTERO_USER_ID", "")
    return f"https://api.zotero.org/users/{user_id}"


def item_exists(title: str) -> bool:
    if not title.strip():
        return False
    base = zotero_base()
    session = http_session()
    response = session.get(
        f"{base}/items",
        headers=zotero_headers(),
        params={"q": title, "qmode": "title", "limit": 5},
        timeout=30,
    )
    if response.status_code != 200:
        return False
    for item in response.json():
        data = item.get("data", {})
        if (data.get("title") or "").strip().lower() == title.strip().lower():
            return True
    return False


def build_tags(record: dict, query: str) -> list[dict[str, str]]:
    tags = [
        {"tag": query},
        {"tag": record.get("language") or "unknown-language"},
        {"tag": record.get("source") or "unknown-source"},
        {"tag": record.get("access_status") or "metadata_only"},
    ]
    for keyword in (record.get("keywords") or [])[:8]:
        tags.append({"tag": keyword})
    return tags


def build_item(record: dict, query: str) -> dict:
    creators = []
    for author in record.get("authors", []):
        parts = author.split()
        if len(parts) >= 2:
            creators.append({"creatorType": "author", "firstName": " ".join(parts[:-1]), "lastName": parts[-1]})
        elif author:
            creators.append({"creatorType": "author", "name": author})
    return {
        "itemType": "journalArticle",
        "title": record.get("title", ""),
        "creators": creators,
        "abstractNote": record.get("abstract", ""),
        "publicationTitle": record.get("journal", ""),
        "date": str(record.get("year") or ""),
        "DOI": record.get("doi", ""),
        "url": record.get("url", ""),
        "tags": build_tags(record, query),
        "extra": f"relevance_note: {record.get('relevance_note', '')}",
    }


def ensure_collection(collection: str) -> str:
    base = zotero_base()
    collection_url = f"{base}/collections"
    session = http_session()
    response = session.get(collection_url, headers=zotero_headers(), params={"q": collection, "qmode": "title"}, timeout=30)
    if response.status_code == 200:
        for item in response.json():
            data = item.get("data", {})
            if data.get("name") == collection:
                return item.get("key", "")

    response = session.post(collection_url, headers=zotero_headers(), json=[{"name": collection}], timeout=30)
    if response.status_code not in (200, 201):
        return ""
    successful = response.json().get("successful", {})
    for _, item in successful.items():
        return item.get("key", "")
    return ""


def create_items(records: list[dict], collection: str, query: str) -> list[dict]:
    base = zotero_base()
    create_url = f"{base}/items"
    collection_key = ensure_collection(collection)
    session = http_session()
    created = []
    for record in records:
        title = record.get("title", "")
        if item_exists(title):
            created.append({"title": title, "status": "skipped_existing"})
            continue
        item_payload = build_item(record, query)
        if collection_key:
            item_payload["collections"] = [collection_key]
        response = session.post(create_url, headers=zotero_headers(), json=[item_payload], timeout=30)
        if response.status_code not in (200, 201):
            created.append({"title": title, "status": "failed", "detail": response.text[:300]})
            continue
        response_data = response.json()
        successful = response_data.get("successful", {})
        for _, item in successful.items():
            key = item.get("key", "")
            created.append({"title": title, "status": "imported", "key": key})
            note_text = record.get("relevance_note", "")
            if record.get("access_status") == "manual_required":
                note_text = f"{note_text}\n需人工下载后补附件。"
            if note_text:
                session.post(
                    create_url,
                    headers=zotero_headers(),
                    json=[{"itemType": "note", "parentItem": key, "note": note_text}],
                    timeout=30,
                )
    return created


def stage_manual_files(records: list[dict], collection: str) -> list[dict]:
    target_dir = MANUAL_DIR / slugify(collection, "collection")
    target_dir.mkdir(parents=True, exist_ok=True)
    staged = []
    for record in records:
        pdf_path = record.get("pdf_path", "")
        if pdf_path and Path(pdf_path).exists():
            destination = target_dir / Path(pdf_path).name
            shutil.copy2(pdf_path, destination)
            staged.append({"title": record.get("title", ""), "pdf": str(destination)})
        else:
            staged.append({"title": record.get("title", ""), "pdf": "", "status": record.get("access_status")})
    manifest_path = target_dir / "manual-import.json"
    write_json(manifest_path, {"collection": collection, "records": records})
    return staged


def main() -> int:
    load_local_env()
    parser = argparse.ArgumentParser(description="Import literature manifest into Zotero or stage a manual import bundle.")
    parser.add_argument("--manifest", type=Path, required=True, help="Manifest JSON path.")
    parser.add_argument("--collection", required=True, help="Logical collection name.")
    parser.add_argument("--mode", choices=["auto", "web_api", "manual"], default="auto", help="Import mode.")
    args = parser.parse_args()

    manifest = read_json(args.manifest)
    records = manifest.get("records", [])
    query = manifest.get("query", args.collection)

    mode = args.mode
    if mode == "auto":
        mode = "web_api" if os.environ.get("ZOTERO_USER_ID") and os.environ.get("ZOTERO_API_KEY") else "manual"

    if mode == "web_api":
        result = {
            "mode": "web_api",
            "created": create_items(records, args.collection, query),
            "manual_files": stage_manual_files(records, args.collection),
        }
    else:
        result = {
            "mode": "manual",
            "manual_files": stage_manual_files(records, args.collection),
        }

    print_json(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

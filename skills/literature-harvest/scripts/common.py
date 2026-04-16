from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


RUNS_DIR = Path(__file__).resolve().parent.parent / "runs"
MANUAL_DIR = Path(__file__).resolve().parent.parent / "manual_import"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


@dataclass
class LiteratureRecord:
    source: str
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    journal: str = ""
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    doi: str = ""
    url: str = ""
    pdf_path: str = ""
    language: str = ""
    access_status: str = "metadata_only"
    relevance_note: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["year"] = self.year or ""
        return payload


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def slugify(value: str, default: str = "record") -> str:
    lowered = value.strip().lower()
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", lowered)
    slug = slug.strip("-")
    return slug or default


def write_json(path: Path, payload: Any) -> Path:
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def parse_record_file(path: Path) -> list[dict[str, Any]]:
    data = read_json(path)
    if isinstance(data, dict) and "records" in data:
        records = data["records"]
    elif isinstance(data, list):
        records = data
    else:
        records = [data]
    return [item if isinstance(item, dict) else {"value": item} for item in records]


def default_output_path(prefix: str, query: str) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    name = slugify(query, prefix)
    return RUNS_DIR / f"{prefix}-{name}.json"


def add_output_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", type=Path, help="Optional explicit JSON output path.")


def http_session():
    import requests

    session = requests.Session()
    session.trust_env = False
    return session


def load_local_env() -> None:
    if not ENV_FILE.exists():
        return
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value

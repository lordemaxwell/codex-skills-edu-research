from __future__ import annotations

import argparse
from collections import Counter
from glob import glob
from pathlib import Path

from common import MANUAL_DIR, RUNS_DIR, add_output_argument, parse_record_file, print_json, slugify, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a manifest from one or more record JSON files.")
    parser.add_argument("--input-glob", default=str(RUNS_DIR / "*.json"), help="Glob for input JSON files.")
    parser.add_argument("--query", required=True, help="Top-level query or collection name.")
    add_output_argument(parser)
    args = parser.parse_args()

    records = []
    for match in sorted(glob(args.input_glob)):
        path = Path(match)
        records.extend(parse_record_file(path))

    counter = Counter(record.get("access_status", "metadata_only") for record in records)
    manifest = {
        "query": args.query,
        "count": len(records),
        "status_counts": dict(counter),
        "manual_import_dir": str(MANUAL_DIR),
        "records": records,
    }
    out_path = args.output or (RUNS_DIR / f"manifest-{slugify(args.query, 'manifest')}.json")
    write_json(out_path, manifest)
    print_json({"output": str(out_path), **manifest})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

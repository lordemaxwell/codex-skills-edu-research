from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

from common import load_local_env


def check_import(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def check_port(host: str, port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.4)
    try:
        return sock.connect_ex((host, port)) == 0
    finally:
        sock.close()


def detect_playwright_cli() -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def main() -> int:
    load_local_env()
    parser = argparse.ArgumentParser(description="Check literature-harvest environment status.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument(
        "--profile-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "profiles" / "default",
        help="Browser profile directory to validate.",
    )
    args = parser.parse_args()

    profile_dir = args.profile_dir
    profile_dir.mkdir(parents=True, exist_ok=True)
    output = {
        "python": sys.executable,
        "python_exists": Path(sys.executable).exists(),
        "playwright_importable": check_import("playwright"),
        "playwright_cli": detect_playwright_cli(),
        "requests_importable": check_import("requests"),
        "bs4_importable": check_import("bs4"),
        "chrome_on_path": bool(shutil.which("chrome") or shutil.which("chromium") or shutil.which("msedge")),
        "browser_channel": os.environ.get("LIT_HARVEST_BROWSER_CHANNEL", "msedge"),
        "profile_dir": str(profile_dir),
        "profile_writable": os.access(profile_dir, os.W_OK),
        "zotero_web_api_configured": bool(os.environ.get("ZOTERO_USER_ID") and os.environ.get("ZOTERO_API_KEY")),
        "zotero_local_port_23119": check_port("127.0.0.1", 23119),
        "manual_import_dir": str(Path(__file__).resolve().parent.parent / "manual_import"),
    }

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for key, value in output.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

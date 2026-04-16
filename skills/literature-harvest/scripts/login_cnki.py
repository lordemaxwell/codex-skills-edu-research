from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from common import load_local_env, print_json


SEARCH_SELECTORS = [
    'input[placeholder*="主题"]',
    'input[placeholder*="检索"]',
    'input.search-input',
    '#txt_search',
    'input[type="text"]',
]


def cnki_ready(page) -> bool:
    if "verify/home" in page.url:
        return False
    if "login" in page.url.lower():
        return False
    title = page.title()
    if "验证" in title or "登录" in title:
        return False
    for selector in SEARCH_SELECTORS:
        locator = page.locator(selector)
        if locator.count():
            return True
    return False


def main() -> int:
    load_local_env()
    parser = argparse.ArgumentParser(description="Open a visible CNKI session and wait for manual login or verification completion.")
    parser.add_argument(
        "--profile-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "profiles" / "cnki",
        help="Persistent browser profile directory.",
    )
    parser.add_argument("--wait-seconds", type=int, default=300, help="How long to wait for CNKI to become ready.")
    parser.add_argument("--start-url", default="https://kns.cnki.net/kns8s/defaultresult/index", help="CNKI page to open.")
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    channel = os.environ.get("LIT_HARVEST_BROWSER_CHANNEL", "msedge")
    with sync_playwright() as p:
        launch_kwargs = {
            "user_data_dir": str(args.profile_dir),
            "headless": False,
            "accept_downloads": True,
        }
        if channel and channel != "chromium":
            launch_kwargs["channel"] = channel
        context = p.chromium.launch_persistent_context(**launch_kwargs)
        page = context.new_page()
        try:
            page.goto(args.start_url, wait_until="domcontentloaded", timeout=60000)
        except Exception:
            pass

        deadline = time.time() + max(args.wait_seconds, 1)
        while time.time() < deadline:
            if page.is_closed():
                break
            if cnki_ready(page):
                print_json(
                    {
                        "ready": True,
                        "url": page.url,
                        "title": page.title(),
                        "profile_dir": str(args.profile_dir),
                        "message": "CNKI session ready. Persistent browser profile saved for later fetches.",
                    }
                )
                context.close()
                return 0
            time.sleep(1)

        print_json(
            {
                "ready": False,
                "url": "" if page.is_closed() else page.url,
                "title": "" if page.is_closed() else page.title(),
                "profile_dir": str(args.profile_dir),
                "message": "Timed out waiting for CNKI login or verification to complete.",
            }
        )
        if not page.is_closed():
            context.close()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

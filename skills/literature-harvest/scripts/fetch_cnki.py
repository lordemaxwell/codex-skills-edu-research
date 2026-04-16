from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from common import LiteratureRecord, add_output_argument, default_output_path, load_local_env, print_json, write_json


SEARCH_SELECTORS = [
    'input[placeholder*="主题"]',
    'input[placeholder*="检索"]',
    'input.search-input',
    '#txt_search',
    'input[type="text"]',
]


def infer_relevance(query: str, title: str, keywords: list[str]) -> str:
    terms = [term for term in query.replace("，", " ").replace(",", " ").split() if term]
    hits = [term for term in terms if term in title or term in "".join(keywords)]
    if hits:
        return f"与中文检索主题直接相关，命中词：{', '.join(hits[:4])}。"
    return "可作为中文相邻主题或政策语境参考。"


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


def wait_for_cnki_ready(page, timeout_seconds: int) -> bool:
    deadline = time.time() + max(timeout_seconds, 1)
    while time.time() < deadline:
        if cnki_ready(page):
            return True
        time.sleep(1)
    return False


def build_record(data: dict, query: str) -> dict:
    record = LiteratureRecord(
        source="cnki",
        title=data.get("title", ""),
        authors=data.get("authors", []),
        year=data.get("year"),
        journal=data.get("journal", ""),
        abstract=data.get("abstract", ""),
        keywords=data.get("keywords", []),
        doi=data.get("doi", ""),
        url=data.get("url", ""),
        pdf_path=data.get("pdf_path", ""),
        language="zh",
        access_status=data.get("access_status", "metadata_only"),
        relevance_note=infer_relevance(query, data.get("title", ""), data.get("keywords", [])),
        extra=data.get("extra", {}),
    )
    return record.to_dict()


def run_fetch(query: str, max_results: int, profile_dir: Path, show_browser: bool, download_pdf: bool) -> list[dict]:
    from playwright.sync_api import TimeoutError, sync_playwright

    results: list[dict] = []
    with sync_playwright() as p:
        channel = os.environ.get("LIT_HARVEST_BROWSER_CHANNEL", "msedge")
        headless = os.environ.get("LIT_HARVEST_CNKI_HEADLESS", "0") == "1" and not show_browser
        launch_kwargs = {
            "user_data_dir": str(profile_dir),
            "headless": headless,
            "accept_downloads": True,
        }
        if channel and channel != "chromium":
            launch_kwargs["channel"] = channel
        context = p.chromium.launch_persistent_context(**launch_kwargs)
        page = context.new_page()
        page.goto("https://kns.cnki.net/kns8s/defaultresult/index", wait_until="domcontentloaded", timeout=60000)

        if not cnki_ready(page) and show_browser:
            wait_for_cnki_ready(page, 300)

        if not cnki_ready(page):
            results.append(
                build_record(
                    {
                        "title": f"CNKI manual action required: {query}",
                        "access_status": "manual_required",
                        "url": page.url,
                        "extra": {"reason": "login_or_verification_required"},
                    },
                    query,
                )
            )
            context.close()
            return results

        search_box = None
        for selector in SEARCH_SELECTORS:
            locator = page.locator(selector)
            if locator.count():
                search_box = locator.first
                break

        if search_box is None:
            results.append(
                build_record(
                    {
                        "title": f"CNKI selector drift: {query}",
                        "access_status": "failed",
                        "url": page.url,
                        "extra": {"reason": "search_box_not_found"},
                    },
                    query,
                )
            )
            context.close()
            return results

        search_box.fill(query)
        search_box.press("Enter")
        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except TimeoutError:
            pass

        cards = page.locator("tbody tr, .result-table-list tr, .knowledge-list li")
        total = min(cards.count(), max_results)
        for index in range(total):
            card = cards.nth(index)
            title_link = card.locator("a").first
            title = title_link.inner_text().strip() if title_link.count() else card.inner_text().splitlines()[0].strip()
            if title.startswith("题名") and "来源" in title and "发表时间" in title:
                continue
            url = title_link.get_attribute("href") if title_link.count() else page.url
            detail_page = context.new_page()
            if url:
                if url.startswith("//"):
                    url = f"https:{url}"
                elif url.startswith("/"):
                    url = f"https://kns.cnki.net{url}"
                detail_page.goto(url, wait_until="domcontentloaded", timeout=60000)
            else:
                title_link.click()
                detail_page.wait_for_load_state("domcontentloaded", timeout=60000)

            abstract = ""
            for selector in [".abstract-text", "#ChDivSummary", ".xx_font"]:
                locator = detail_page.locator(selector)
                if locator.count():
                    abstract = locator.first.inner_text().strip()
                    break

            journal = ""
            for selector in [".source", "a.host-name", ".top-tip span"]:
                locator = detail_page.locator(selector)
                if locator.count():
                    journal = locator.first.inner_text().strip()
                    break

            keywords = []
            for selector in ['a[data-type="keyword"]', ".keywords a", "#keyword a"]:
                locator = detail_page.locator(selector)
                if locator.count():
                    keywords = [text.strip() for text in locator.all_inner_texts() if text.strip()]
                    break

            authors = []
            for selector in [".author a", "#authorpart a", ".row a"]:
                locator = detail_page.locator(selector)
                if locator.count():
                    authors = [text.strip() for text in locator.all_inner_texts() if text.strip()]
                    if authors:
                        break

            year = None
            detail_text = detail_page.locator("body").inner_text()
            for token in detail_text.split():
                if token.isdigit() and len(token) == 4 and token.startswith(("19", "20")):
                    year = int(token)
                    break

            pdf_path = ""
            access_status = "metadata_only"
            download_button = detail_page.locator('a:has-text("下载"), button:has-text("下载"), a[href*="download"]').first
            if download_pdf and download_button.count():
                with detail_page.expect_download(timeout=15000) as download_info:
                    download_button.click()
                download = download_info.value
                target = Path(__file__).resolve().parent.parent / "downloads" / download.suggested_filename
                target.parent.mkdir(parents=True, exist_ok=True)
                download.save_as(str(target))
                pdf_path = str(target)
                access_status = "downloaded"
            elif download_button.count():
                access_status = "manual_required"

            results.append(
                build_record(
                    {
                        "title": title,
                        "authors": authors,
                        "year": year,
                        "journal": journal,
                        "abstract": abstract,
                        "keywords": keywords,
                        "doi": "",
                        "url": detail_page.url,
                        "pdf_path": pdf_path,
                        "access_status": access_status,
                    },
                    query,
                )
            )
            detail_page.close()

        context.close()
    return results


def main() -> int:
    load_local_env()
    parser = argparse.ArgumentParser(description="Fetch CNKI metadata with Playwright.")
    parser.add_argument("--query", required=True, help="CNKI search query.")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum number of records.")
    parser.add_argument("--show-browser", action="store_true", help="Show the browser window for login and inspection.")
    parser.add_argument("--download-pdf", action="store_true", help="Attempt PDF download when a button is visible.")
    parser.add_argument(
        "--profile-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "profiles" / "cnki",
        help="Persistent browser profile directory.",
    )
    add_output_argument(parser)
    args = parser.parse_args()

    records = run_fetch(args.query, args.max_results, args.profile_dir, args.show_browser, args.download_pdf)
    out_path = args.output or default_output_path("fetch-cnki", args.query)
    write_json(out_path, {"query": args.query, "records": records})
    print_json({"output": str(out_path), "count": len(records), "records": records})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

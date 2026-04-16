from __future__ import annotations

import argparse
import os
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from common import LiteratureRecord, add_output_argument, default_output_path, print_json, write_json


PUBLISHER_MAP = {
    "sciencedirect.com": "elsevier",
    "springer.com": "springer",
    "link.springer.com": "springer",
    "wiley.com": "wiley",
    "onlinelibrary.wiley.com": "wiley",
    "tandfonline.com": "taylor_and_francis",
    "sagepub.com": "sage",
    "journals.sagepub.com": "sage",
    "jstor.org": "jstor",
    "www.jstor.org": "jstor",
}


def detect_publisher(url: str) -> str:
    host = urlparse(url).netloc.lower()
    for domain, publisher in PUBLISHER_MAP.items():
        if host.endswith(domain):
            return publisher
    return "publisher"


def infer_relevance(url: str, abstract: str) -> str:
    publisher = detect_publisher(url)
    if abstract:
        return f"来自 {publisher} 页面，可用于补全文献元数据并判断获取路径。"
    return f"来自 {publisher} 页面，建议结合开放检索结果判断其研究价值。"


def meta_content(soup: BeautifulSoup, names: list[str], attrs: tuple[str, ...] = ("name", "property")) -> str:
    for attr in attrs:
        for name in names:
            tag = soup.find("meta", attrs={attr: name})
            if tag and tag.get("content"):
                return tag["content"].strip()
    return ""


def list_meta(soup: BeautifulSoup, name: str) -> list[str]:
    values = []
    for tag in soup.find_all("meta", attrs={"name": name}):
        content = tag.get("content", "").strip()
        if content:
            values.append(content)
    return values


def fetch_page(url: str, profile_dir: Path, show_browser: bool, download_pdf: bool) -> dict:
    from playwright.sync_api import TimeoutError, sync_playwright

    with sync_playwright() as p:
        channel = os.environ.get("LIT_HARVEST_BROWSER_CHANNEL", "msedge")
        launch_kwargs = {
            "user_data_dir": str(profile_dir),
            "headless": not show_browser,
            "accept_downloads": True,
        }
        if channel and channel != "chromium":
            launch_kwargs["channel"] = channel
        context = p.chromium.launch_persistent_context(**launch_kwargs)
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except TimeoutError:
            pass

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        title = meta_content(soup, ["citation_title", "dc.title", "og:title"]) or (soup.title.string.strip() if soup.title else "")
        abstract = meta_content(soup, ["citation_abstract", "description", "dc.description", "og:description"])
        authors = list_meta(soup, "citation_author")
        journal = meta_content(soup, ["citation_journal_title", "dc.source"])
        year_text = meta_content(soup, ["citation_publication_date", "citation_date", "dc.date"])
        year = None
        for chunk in year_text.replace("/", "-").split("-"):
            if chunk.isdigit() and len(chunk) == 4:
                year = int(chunk)
                break
        doi = meta_content(soup, ["citation_doi", "dc.identifier", "doi"])
        keywords = list_meta(soup, "citation_keywords")
        pdf_path = ""
        access_status = "metadata_only"

        pdf_selectors = [
            'a[href$=".pdf"]',
            'a[data-test="pdf-link"]',
            'a:has-text("Download PDF")',
            'a:has-text("PDF")',
            'button:has-text("PDF")',
        ]
        pdf_button = None
        for selector in pdf_selectors:
            locator = page.locator(selector)
            if locator.count():
                pdf_button = locator.first
                break

        if pdf_button and download_pdf:
            with page.expect_download(timeout=15000) as download_info:
                pdf_button.click()
            download = download_info.value
            target = Path(__file__).resolve().parent.parent / "downloads" / download.suggested_filename
            target.parent.mkdir(parents=True, exist_ok=True)
            download.save_as(str(target))
            pdf_path = str(target)
            access_status = "downloaded"
        elif pdf_button:
            access_status = "manual_required"

        record = LiteratureRecord(
            source="publisher",
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            abstract=abstract,
            keywords=keywords,
            doi=doi.replace("https://doi.org/", ""),
            url=page.url,
            pdf_path=pdf_path,
            language="en",
            access_status=access_status,
            relevance_note=infer_relevance(url, abstract),
            extra={"publisher": detect_publisher(page.url)},
        )
        context.close()
        return record.to_dict()


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch publisher metadata and optional PDF access state.")
    parser.add_argument("--url", required=True, help="Publisher article URL.")
    parser.add_argument("--show-browser", action="store_true", help="Show browser for login and inspection.")
    parser.add_argument("--download-pdf", action="store_true", help="Attempt to download PDF if visible.")
    parser.add_argument(
        "--profile-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "profiles" / "publisher",
        help="Persistent browser profile directory.",
    )
    add_output_argument(parser)
    args = parser.parse_args()

    record = fetch_page(args.url, args.profile_dir, args.show_browser, args.download_pdf)
    out_path = args.output or default_output_path("fetch-publisher", record.get("title") or args.url)
    write_json(out_path, {"records": [record]})
    print_json({"output": str(out_path), "records": [record]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

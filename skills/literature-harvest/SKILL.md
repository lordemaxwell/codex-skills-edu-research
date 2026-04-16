---
name: literature-harvest
description: Harvest education and economics literature from CNKI, open metadata sources, and English publisher sites into Zotero-ready workflows. Use when Codex needs to search topic-relevant papers, expand to adjacent innovative literature, extract CNKI or publisher metadata with browser automation, classify download status, prepare manual-download fallbacks, or import records into Zotero.
---

# Literature Harvest

Use this skill to run a practical literature collection workflow for education and economics topics. Favor stable metadata capture, clear access-state classification, and Zotero landing over brittle promises of universal full-text automation.

## Quick Start

Run all scripts through the wrapper:

```powershell
& 'D:\Python\Python311\python.exe' scripts\run.py check_env --json
& 'D:\Python\Python311\python.exe' scripts\run.py search_open --query "school finance inequality" --max-results 10
```

If the wrapper cannot find a usable Python interpreter, set `LIT_HARVEST_PYTHON` to an absolute `python.exe` path and rerun.

## Workflow

### 1. Check environment first

Run:

```powershell
& 'D:\Python\Python311\python.exe' scripts\run.py check_env --json
```

Confirm:
- a usable Python interpreter exists
- Playwright is importable
- Chromium is installed or installable
- the browser profile directory is writable
- Zotero import mode is configured or a manual fallback directory is available

If `check_env` reports a missing dependency, run:

```powershell
& 'D:\Python\Python311\python.exe' scripts\run.py setup_environment
```

### 2. Search open metadata sources first

Use open sources to build a candidate set and capture high-quality metadata before hitting CNKI or publisher pages:

```powershell
& 'D:\Python\Python311\python.exe' scripts\run.py search_open --query "双减 政策评估" --language zh --max-results 15
& 'D:\Python\Python311\python.exe' scripts\run.py search_open --query "school finance inequality" --language en --max-results 15 --sources openalex crossref semantic_scholar
```

Use these results to identify:
- directly relevant papers
- review or methods papers worth reading for inspiration
- candidate DOI or publisher URLs for downstream fetching

Read [references/relevance-rules.md](references/relevance-rules.md) when the request emphasizes novelty, inspiration, or adjacent literatures.

### 3. Use source-specific fetchers

For CNKI:

```powershell
& 'D:\Python\Python311\python.exe' scripts\run.py fetch_cnki --query "职业教育 产教融合" --max-results 10 --show-browser
```

Use browser-visible mode when:
- login is required
- institutional access redirects appear
- CAPTCHA or unusual verification appears
- selectors drift and you need to inspect the live page

For publisher pages:

```powershell
& 'D:\Python\Python311\python.exe' scripts\run.py fetch_publisher --url "https://link.springer.com/article/10.1007/..." --download-pdf
```

The publisher fetcher is designed to:
- detect supported publishers
- extract normalized metadata
- attempt PDF capture only when a reachable button exists
- mark inaccessible full text as `manual_required` rather than failing the record

Read [references/source-matrix.md](references/source-matrix.md) when choosing between automation and manual takeover.

### 4. Build a manifest and import into Zotero

Combine record files into one manifest:

```powershell
& 'D:\Python\Python311\python.exe' scripts\run.py build_manifest --input-glob "runs\*.json" --query "school finance inequality"
```

Import the manifest:

```powershell
& 'D:\Python\Python311\python.exe' scripts\run.py import_zotero --manifest "runs\manifest.json" --collection "school-finance-inequality"
```

Import behavior:
- use Zotero Web API when `ZOTERO_USER_ID` and `ZOTERO_API_KEY` are configured
- create metadata records, tags, and notes
- if a local PDF cannot be uploaded automatically, stage it for manual attachment and record the path
- keep `manual_required` items visible in the output instead of silently dropping them

Read [references/zotero-mapping.md](references/zotero-mapping.md) for field mapping and fallback behavior.

### 5. Treat manual download as a first-class path

Do not keep retrying brittle download flows if:
- CNKI requires repeated verification
- institutional login must be completed by the user
- the site serves the PDF through a protected viewer
- the publisher blocks scripted downloads

Instead:
- capture metadata and stable URLs
- set `access_status` to `manual_required`
- tell the user exactly what to download
- rerun `import_zotero` after the PDF is available locally

See [references/workflows.md](references/workflows.md) for the full end-to-end flow.

## Output Contract

All scripts should converge on this minimum record shape:

```json
{
  "source": "cnki|crossref|openalex|publisher",
  "title": "",
  "authors": [],
  "year": 2024,
  "journal": "",
  "abstract": "",
  "keywords": [],
  "doi": "",
  "url": "",
  "pdf_path": "",
  "language": "zh|en",
  "access_status": "downloaded|metadata_only|manual_required|failed",
  "relevance_note": ""
}
```

Always preserve `relevance_note`. When the user asks for “有启发性”的文献, explain briefly why the paper matters for the current topic rather than only listing keywords.

## Resources

- `scripts/check_env.py`: environment and dependency checks
- `scripts/search_open.py`: search OpenAlex, Crossref, Semantic Scholar, and PubMed
- `scripts/fetch_cnki.py`: CNKI browser-driven metadata extraction
- `scripts/fetch_publisher.py`: publisher-page metadata extraction and controlled PDF attempts
- `scripts/build_manifest.py`: merge records into a run manifest
- `scripts/import_zotero.py`: Zotero import and manual-attachment staging
- `references/workflows.md`: operating procedures
- `references/source-matrix.md`: source capability matrix
- `references/relevance-rules.md`: topic relevance and inspiration heuristics
- `references/zotero-mapping.md`: import mapping and fallback notes

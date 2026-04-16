# Workflows

## 1. Open Search to CNKI

1. Run `search_open.py` to map the topic and identify adjacent terms.
2. Convert the strongest Chinese topic terms into a CNKI query.
3. Run `fetch_cnki.py` with `--show-browser` when login or verification may appear.
4. If metadata is captured but PDF is unavailable, mark the record `manual_required`.
5. Merge results with `build_manifest.py`.
6. Import through `import_zotero.py`.

## 2. Open Search to Publisher Page

1. Run `search_open.py` with `openalex`, `crossref`, and `semantic_scholar`.
2. Select candidate DOI or publisher URLs.
3. Run `fetch_publisher.py` on the direct article page.
4. Only attempt `--download-pdf` when you already have access or want to test the button state.
5. If the site serves a viewer, paywall, or SSO wall, keep the metadata and switch to manual download.

## 3. Manual Download Fallback

Use this branch when:
- CNKI requires repeated human verification
- the institution login is only stable in a visible browser
- a publisher blocks scripted PDF downloads
- the article is available only through a protected viewer

Procedure:
1. Keep metadata, DOI, and landing URL.
2. Set `access_status` to `manual_required`.
3. Tell the user which files must be downloaded manually.
4. Place manually downloaded PDFs into the skill's `downloads/` folder or another known path.
5. Rerun `import_zotero.py` so the record and local file paths are staged together.

## 4. Zotero Landing

Preferred order:
1. Web API import for metadata and notes.
2. Manual attachment staging for PDFs that cannot be uploaded automatically.
3. Keep a manifest file so records are never lost between automated and manual steps.

# Zotero Mapping

## Record to Zotero Item

| Record Field | Zotero Field |
|---|---|
| `title` | `title` |
| `authors` | `creators` |
| `journal` | `publicationTitle` |
| `year` | `date` |
| `abstract` | `abstractNote` |
| `doi` | `DOI` |
| `url` | `url` |
| `relevance_note` | child note or `extra` |

## Tags

Always add:
- query or collection name
- language
- source
- access status

Add up to 8 keywords when available.

## Access Status Handling

- `downloaded`: create or stage a metadata record and preserve the local PDF path.
- `metadata_only`: import metadata now; attachment can be added later.
- `manual_required`: import metadata plus a note saying the PDF must be added manually.
- `failed`: keep the item in the manifest but do not silently import broken placeholders.

## Practical Limitation

The bundled `import_zotero.py` script supports:
- direct metadata import through Zotero Web API
- note creation
- manual attachment staging for local PDFs

If the user has not configured `ZOTERO_USER_ID` and `ZOTERO_API_KEY`, use manual mode and keep the manifest plus files ready for later import.

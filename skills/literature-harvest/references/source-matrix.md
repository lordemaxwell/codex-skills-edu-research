# Source Matrix

| Source | Best Use | Automation Level | Full Text Expectation | When to Switch to Manual |
|---|---|---|---|---|
| CNKI | Chinese education and economics journals, dissertations, policy context | Medium | Unstable; depends on login, institution, and page changes | Verification loops, no stable download button, or repeated redirects |
| OpenAlex | English candidate discovery, related work, metadata enrichment | High | Metadata only by design | Full text needed |
| Crossref | DOI lookup, citation metadata, journal identifiers | High | Metadata only by design | Full text needed |
| Semantic Scholar | Broad English discovery and abstract retrieval | High | Metadata only by design | Full text needed |
| PubMed | Health-adjacent education or economics topics | High | Metadata only by design | Full text needed |
| Elsevier / ScienceDirect | Publisher metadata and access-state check | Medium | Sometimes accessible if logged in | PDF viewer or paywall blocks scripted download |
| Springer | Publisher metadata and download-state check | Medium | Often exposes a direct PDF button when entitled | Institutional redirect or dynamic viewer blocks access |
| Wiley | Publisher metadata and download-state check | Medium | Varies by journal and entitlement | SSO wall or blocked PDF button |
| Taylor & Francis | Publisher metadata and download-state check | Medium | Varies | Viewer or anti-bot behavior |
| SAGE | Publisher metadata and download-state check | Medium | Varies | Viewer or login wall |
| JSTOR | Stable metadata, limited scripted PDF success | Low to medium | Often better handled manually | Login wall or PDF request flow requires full user session |

## Notes

- Treat metadata capture as the guaranteed outcome.
- Treat PDF capture as opportunistic, not mandatory.
- Keep unsupported publishers in the same pipeline by classifying them as generic `publisher`.

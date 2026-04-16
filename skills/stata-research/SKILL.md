---
name: stata-research
description: Stata coding, debugging, and empirical economics workflows for education economics and applied micro research. Use when Codex needs to write or revise .do files, inspect or clean survey and panel data, run descriptive statistics, fixed effects, DiD, event study, IV, RD, matching, export tables or graphs, or diagnose Stata errors and suspicious empirical results.
---

# Stata Research

Use this skill to produce Stata workflows that are executable, auditable, and paper-oriented. Optimize for education economics and applied micro tasks instead of generic software tutorials.

## Quick Routing

- For data inspection, recoding, merging, reshaping, and variable construction, read `references/stata-core.md` and `references/data-cleaning.md`.
- For baseline regressions, panel setup, fixed effects, and clustered inference, read `references/panel-and-fe.md`.
- For DiD, event study, IV, RD, and matching, read `references/causal-designs.md`.
- For regression tables, coefficient plots, and export workflows, read `references/output-and-graphs.md`.
- For Stata errors, silent logic bugs, or suspicious estimates, read `references/debugging.md`.
- For full paper-style empirical workflows and replication-oriented organization, read `references/paper-workflow.md`.
- For user-written package choice or installation assumptions, read `references/packages.md`.

## Core Workflow

1. Reconstruct the empirical task before writing code: unit of observation, sample, treatment, timing, outcome, controls, and identification logic.
2. Inspect existing files when available. Do not invent variable names, merge keys, or time variables if the artifacts can be read.
3. Choose the lightest design that answers the question. State the identifying assumption that makes the design credible.
4. Write code as a complete `.do` workflow when possible: setup, cleaning, estimation, export, and validation checks.
5. Check common failure points before trusting results: missing values, duplicates, merge mismatches, impossible treatment timing, wrong clustering level, collinearity from fixed effects, and omitted base periods.
6. Return both code and a short explanation of why the design and command choice answer the user's question.

## Output Rules

- Prefer complete code blocks over scattered command fragments.
- Use `local` macros for paths, variable bundles, and repeated options.
- Split code into labeled sections such as `data prep`, `estimation`, and `export`.
- Add short comments only where they help interpret non-obvious research logic.
- When inference matters, specify `vce(cluster ...)` or explain why another variance estimator is appropriate.
- When execution is unavailable, provide best-effort code plus a short checklist for what the user should verify after running it.

## Guardrails

- Never treat Stata missing values such as `.` as zero. Numeric missing values sort above real numbers.
- After `merge`, inspect `_merge` before dropping rows or claiming the merge worked.
- Before panel estimators, verify that panel id and time uniquely identify observations where required.
- For DiD and event study, define treatment timing and the omitted reference period explicitly.
- For IV, explain the first stage, exclusion restriction, and clustering choice rather than presenting `ivregress` as self-justifying.
- For RD, make bandwidth, polynomial order, and manipulation checks explicit.
- Distinguish code that is source-grounded from assumptions inferred because files or metadata are missing.

## Preferred Style

- Favor factor-variable notation such as `i.year` and `c.x##i.treat` over manually generated dummies unless there is a clear reason not to.
- Use `isid`, `duplicates report`, `tab`, `summarize, detail`, and `codebook` early when data structure is uncertain.
- Keep destructive steps reversible where possible with `preserve`/`restore` or explicit intermediate outputs.
- Prefer readable, publication-oriented defaults over clever compact code.

## Typical Requests

- "Write a Stata `.do` file to clean CHFS-style household data and build treatment indicators."
- "Help me run a two-way fixed effects model with county and year fixed effects."
- "Why does my event-study graph look wrong after treatment timing coding?"
- "Export baseline and robustness regressions into one table for a paper draft."
- "Check whether this IV setup is coherent and rewrite the code."

## References

- `references/stata-core.md`
- `references/data-cleaning.md`
- `references/panel-and-fe.md`
- `references/causal-designs.md`
- `references/output-and-graphs.md`
- `references/debugging.md`
- `references/paper-workflow.md`
- `references/packages.md`

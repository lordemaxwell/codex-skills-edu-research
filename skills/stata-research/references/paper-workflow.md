# Paper Workflow

Use this reference when the task is to build or revise a paper-style empirical workflow instead of a single command.

## Recommended Layout

- `data/raw/`
- `data/clean/`
- `do/`
- `results/tables/`
- `results/figures/`
- `logs/`

## Preferred .do Structure

1. Environment setup
2. Raw-to-clean data preparation
3. Main sample construction
4. Baseline regressions
5. Mechanism or heterogeneity analysis
6. Robustness checks
7. Table and figure export

## Research-Oriented Output

- Name outputs by research role, not by vague version labels.
- Separate baseline, mechanism, and robustness sections.
- Keep a concise note on identification assumptions near the estimation block.
- When asked to help with a paper draft, translate the model into both code and a one-paragraph methods explanation.

## Reproducibility Rules

- Avoid hidden manual steps.
- Save intermediate cleaned datasets when the pipeline is expensive or fragile.
- Keep file paths centralized in one setup section.
- Prefer deterministic exports over interactive copy-paste from the Stata results window.

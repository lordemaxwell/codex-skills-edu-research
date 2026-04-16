# Output and Graphs

Use this reference for regression tables, coefficient plots, and publication-oriented exports.

## Table Workflow

- Use `eststo` plus `esttab` when producing multiple comparable models.
- Use `outreg2` only if the project already depends on it.
- Keep variable labels and notes aligned with the paper's terminology.

### Example

```stata
eststo clear
eststo m1: reghdfe y treat, absorb(id year) vce(cluster id)
eststo m2: reghdfe y treat controls, absorb(id year) vce(cluster id)

esttab m1 m2 using "results/baseline.rtf", ///
    replace se star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N r2, labels("Obs." "R-squared"))
```

## Graph Workflow

- Use `coefplot` for event-study style coefficient plots when available.
- Use `binscatter` or `binsreg` only when the estimand and residualization logic are clear.
- Export figures with deterministic filenames and formats.

```stata
graph export "results/fig_event_study.png", replace width(2000)
```

## Output Rules

- Do not mix baseline, mechanism, and robustness models in one table unless the user asks for that comparison.
- Always verify that the exported sample matches the reported regression sample.
- If a package is unavailable, provide a built-in fallback instead of failing silently.

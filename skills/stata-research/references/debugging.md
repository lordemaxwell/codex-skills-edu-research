# Debugging

Use this reference when Stata code fails or the estimates look implausible.

## Distinguish Error Types

- Syntax error: command does not run.
- Data structure error: ids, time, or types are inconsistent.
- Logic error: code runs but measures the wrong sample or treatment.
- Identification error: model runs but the causal claim is not supported.

## Common Failure Patterns

- `variable not found`: wrong dataset stage, spelling, or renamed field.
- `repeated time values within panel`: `xtset` keys are not unique.
- Perfect collinearity or omitted regressors: fixed effects absorb the variation.
- Huge treatment effects with tiny standard errors: wrong clustering, duplicate observations, or coding error in treatment timing.
- Empty cells in event study: treatment timing or support window is wrong.

## Debug Sequence

1. Reproduce the exact failing command.
2. Print the relevant variables with `list` or `tab`.
3. Check ids, duplicates, and missingness.
4. Compare the intended sample to the realized sample.
5. Check whether the treatment variable varies within the absorbed fixed effects.
6. Only after data checks, change the estimator.

## Minimal Diagnostics

```stata
count
count if e(sample)
tab treat if e(sample), missing
sum outcome treat controls if e(sample), detail
duplicates report id year
```

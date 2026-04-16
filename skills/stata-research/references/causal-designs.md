# Causal Designs

Use this reference for DiD, event study, IV, RD, and matching.

## Difference-in-Differences

Minimum questions to answer before writing code:

1. What is the treated unit?
2. When does treatment start?
3. Is treatment staggered?
4. What is the control group?
5. What makes parallel trends plausible?

### Simple DiD Skeleton

```stata
gen post = year >= policy_year if policy_year < .
gen did = treat * post
reghdfe outcome did controls, absorb(id year) vce(cluster id)
```

### Event Study Skeleton

```stata
gen rel_year = year - first_treat_year
forvalues k = -4/4 {
    gen evt_`k' = rel_year == `k'
}
drop evt_-1
reghdfe outcome evt_* controls, absorb(id year) vce(cluster id)
```

Never omit the reference period silently. State it.

## IV

```stata
ivreghdfe outcome controls (endog = instrument), absorb(id year) cluster(id)
```

Explain:

- Why the instrument shifts the endogenous regressor
- Why exclusion is plausible
- Why the clustering level matches the source of identifying variation

## RD

Prefer `rdrobust` when available. Report cutoff, bandwidth logic, polynomial choice, and manipulation checks.

## Matching

Use matching for balance improvement or selection-on-observables designs only when the identifying assumption is defensible. Report post-match balance, not just treatment effects.

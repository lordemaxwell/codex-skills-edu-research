# Panel and Fixed Effects

Use this reference for baseline regressions, panel setup, and fixed effects models.

## Panel Setup

```stata
xtset id year
xtdescribe
```

Check whether the panel is balanced only if the design requires it. Do not assume balanced panels are necessary.

## Baseline FE Pattern

```stata
reghdfe outcome treat controls, absorb(id year) vce(cluster id)
```

If `reghdfe` is unavailable, fall back carefully:

```stata
xtreg outcome treat controls i.year, fe vce(cluster id)
```

## Decision Rules

- Use entity and time fixed effects when omitted heterogeneity plausibly varies along both dimensions.
- Cluster at the level of treatment assignment or serial correlation risk, not mechanically at the individual level.
- When treatment varies at a higher level such as county or school, clustering below that level is usually indefensible.
- If adding fixed effects absorbs the treatment, explain the identification problem rather than hiding the dropped variable.

## Typical Extensions

- Heterogeneity: `c.treat##i.female`
- Nonlinear exposure: `c.exposure##c.exposure`
- Weights: document whether they are probability weights or analytic weights before using `pweight` or `aweight`.

## Checks to Report

- Number of observations
- Number of panels or clusters
- Whether treatment survives fixed effects
- Whether the sample changed across specifications

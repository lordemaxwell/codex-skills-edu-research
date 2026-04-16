# Packages

Use this reference when package availability matters.

## Preferred User-Written Packages

- `reghdfe` for high-dimensional fixed effects
- `ivreghdfe` for IV with absorbed fixed effects
- `ftools` as a dependency for `reghdfe`
- `estout` or `esttab` for tables
- `outreg2` when the project already uses it
- `coefplot` for coefficient graphs
- `rdrobust` for regression discontinuity
- `ivreg2` for richer IV diagnostics
- `csdid` for staggered DiD when appropriate
- `did_multiplegt` when the design specifically calls for it
- `winsor2` only when winsorization is substantively defensible

## Package Policy

- Do not assume a user-written package exists unless the project context suggests it or the user confirms installation.
- If a package is missing, offer `ssc install` commands plus a built-in fallback where possible.
- Prefer consistency with the existing project over forcing a favorite package.

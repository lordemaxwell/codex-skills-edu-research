# Stata Core

Use this reference when the task involves basic Stata syntax, data inspection, or safe code structure.

## Default Pattern

```stata
version 18
clear all
set more off

local data_in  "data/raw/example.dta"
local data_out "data/clean/example_clean.dta"

use "`data_in'", clear

* inspect first
describe
codebook id year
summarize outcome treat x1 x2, detail
tab year
```

## Safe Habits

- Use `local` rather than globals unless the project clearly relies on globals.
- Prefer `generate` for new variables and `replace` only after checking the existing values.
- Prefer factor-variable notation for interactions and nonlinear terms.
- Use `capture confirm variable varname` before referencing uncertain variables.
- Use `tempvar` and `tempfile` for throwaway intermediates.

## High-Risk Stata Behaviors

- Numeric missing values `.` `.a` `.b` are larger than any real number.
- `if x > 0` includes missing values unless you also exclude them with `& x < .`.
- String numerics often require `destring`, while labeled numerics may require `decode`.
- `egen` and `gen` are not interchangeable. Use `egen` only for functions that need it.

## Minimal Audit Commands

```stata
isid id year
duplicates report id year
misstable summarize
tab treat, missing
tab year treat, missing
assert inrange(share, 0, 1) if share < .
```

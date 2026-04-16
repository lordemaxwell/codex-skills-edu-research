# Data Cleaning

Use this reference when cleaning survey, administrative, or panel data.

## Standard Sequence

1. Verify identifiers and unit of observation.
2. Inspect missingness and impossible values.
3. Harmonize types with `destring`, `encode`, `decode`, or `tostring`.
4. Resolve duplicates before merge or reshape.
5. Merge only after asserting key structure on both sides.
6. Re-check sample counts after every irreversible filter.

## Merge Pattern

```stata
use household_panel, clear
isid hhid year
merge 1:1 hhid year using controls_panel
tab _merge
assert _merge != 2
drop if _merge == 2
drop _merge
```

## Common Tasks

- Use `reshape long` or `reshape wide` only after checking stub names and id uniqueness.
- Use `egen group()` for composite ids when raw keys are string-heavy.
- Use `bysort id (year): gen first_treat_year = year if treat == 1` plus carry-forward logic for treatment timing.
- Use `collapse` only on a copy or after saving a pre-collapse dataset.

## Silent Bug Checklist

- Did a merge create many unmatched rows?
- Did a filter accidentally keep missing values?
- Did `xtset` fail because id-time pairs are not unique?
- Did recoding collapse meaningful categories?
- Did a winsorization or trimming rule remove the treated tail disproportionately?

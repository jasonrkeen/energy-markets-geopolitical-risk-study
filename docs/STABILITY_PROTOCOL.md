# Stability review protocol - frozen before this review's estimates

2026-11-11. Exploratory follow-up to an already inspected sample. No new confirmatory or forecasting claim.

Keep October 2000-March 2026 (306 months), EIA spot, publisher monthly GPR, and the baseline unchanged. Report all checks below without selecting a preferred model by significance.

- Three equal contiguous 102-month periods; HAC(6) intervals.
- Rolling 120-month windows every 12 months, plus the final window if off-grid; overlapping estimates are descriptive, not independent tests.
- A single pooled model interacting intercept and all three regressors with the second and third period indicators. HAC(6) Wald tests for equal oil slopes (two restrictions) and equal all coefficients (eight restrictions); Holm across these two tests only, separately from the existing eleven GPR tests.
- Separately exclude September 2008-June 2009, March-June 2020, and February-June 2022. Use actual-calendar HAC(6); retain baseline alongside all exclusions.
- Add one lagged XLE return, already available on the same 306 months. Report oil interval and residual Ljung-Box lag 12 for both models. The dynamic-model diagnostic subtracts one degree of freedom and is an approximate diagnostic, not a specification-selection rule.
- Audit source-date mismatches, endpoint age, and missing observations on the fixed sample. Retain the common-date sensitivity. Do not infer an exchange holiday calendar or synchronized intraday observations from available quotes.

No holdout is created from already inspected observations. A non-rejection of a stability test does not establish stable parameters. Crisis exclusions change the estimand and sample. HAC inference does not repair omitted variables or causal identification.

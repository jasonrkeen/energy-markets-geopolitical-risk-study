# Version 2 findings and red-team report

2026-10-25 local review. **Share with caveats for exploratory association research; exact historical reproduction remains partial.** Base commit: `89b692ca5cb6412a283a82c7a55c33fceb6412f4`. Original notebook, retained data and V1 outputs were preserved; corrections are on a review branch.

## What was reproduced

All 33 original code cells executed using a cached current Yahoo vintage, truncated to April 28, 2026, inside a separate output sandbox. The final replay has **308 observations**, **R² 0.575074**, **oil beta 0.323027**, **market beta 0.751842**, and **GPR p=0.397925**. The saved notebook reported approximately 0.575, 0.3231, 0.7519 and 0.396. The small mismatch is retained, not rounded away as exact replication.

The archived XLE monthly returns independently equal log-price differences to maximum absolute error **5.42e-16**. Using only the archived XLE and GPR inputs reproduces the original simple model: 328 observations, GPR coefficient 7.56757e-06 and p=0.923188. Across the fresh replay, maximum XLE log-return difference from the archive is 1.343e-06; the five scenario outputs differ by at most 0.002006 percentage points. Missing original oil/market daily downloads and the unrecorded original environment prevent a stronger reproduction claim. `v1_audit.json` records hashes and scope.

## Supported Version 2 results

The retained workbook ends April 27; the notebook ran April 28 while labeling observations April 30. V2 therefore ends **March 2026**. It uses explicit adjusted XLE, S&P price-index returns, GPR calendar-day means and an explicitly qualified oil-price proxy. The baseline has 307 completed months; the matched comparison sample has 306, October 2000–March 2026, after requiring a lagged oil observation.

On that common sample, the XLE model has **R² 0.589227**. HAC(6) oil beta is **0.320835**, 95% CI **[0.228302, 0.413369]**; market beta is **0.782208**, CI **[0.601121, 0.963295]**. The GPR coefficient per 100 index points is **0.007699**, CI **[-0.000426, 0.015824]**, p=**0.063205**. This is about 0.77 log percentage points per 100 GPR points, conditional on the model; it is not a causal effect.

- GPR p-values in the same baseline range from **0.063 to 0.126** across HAC(3/6/12) and HC3. With all 307 eligible months, HAC(6) p=0.0927. No cutoff should be treated as a stable discovery.
- The GPR–oil regression controlling for market return gives p=**0.8405**. Lagged-only joint GPR tests give p=**0.7385** for oil and **0.7376** for XLE. These are in-sample associations, not validated forecast tests.
- One contemporaneous GPR coefficient in the dynamic XLE model has an unadjusted p=**0.0123**, but its joint three-term GPR test is p=**0.0705**. None of eleven HAC(6) joint GPR tests rejects at 5% after Holm correction (smallest adjusted p≈0.551). Reporting only the individual significant term would misrepresent the evidence.
- Oil/equity month-end source dates differ in November 2002, November 2003 and December 2004. Requiring the same last available date produces oil beta **0.322211**, market beta **0.777754**, GPR p=**0.0618**, and R² **0.588733**. This small numerical difference does not establish identical trading calendars or synchronous intraday pricing.
- Excluding March–June 2020 gives oil beta **0.3698**, market beta **0.7123**, GPR p=**0.1570**, using HC3 on 302 observations. This illustrates sensitivity to the crisis window; it is not a preferred result selected after inspecting significance.
- Residual Ljung–Box lag-12 p=**0.0171** indicates remaining serial dependence. HAC addresses uncertainty under its assumptions, not omitted dynamics, instability or identification.

## Red-team findings and remedies

1. **P1 — Unsupported mechanism in the old README.** A nonsignificant GPR coefficient plus a positive oil coefficient does not identify mediation. **Fixed:** the current README reports conditional associations, both supportive and null comparisons, and explicitly disclaims mediation. The historical README remains available as evidence.
2. **P1 — Partial month and unspecified adjustment conventions.** V1 mixes 27 GPR days with a market month ending April 28; XLE defaults and explicitly unadjusted companies are not comparable total-return conventions. **Fixed:** completed-month cutoff, explicit fields and same-sample sensitivities. Company ranking claims are not carried forward.
3. **P1 — Source provenance and reproducibility.** The original daily market downloads, retrieval receipts and package versions are absent; the GPR workbook has no historical receipt. **Mitigated, not resolved:** current-vintage cache, checksums, software lock, numerical replay deltas and source-date ledger. The original-vintage claim remains blocked.
4. **P1 — Futures and return interpretation.** The fresh CL=F series includes **-37.630001 on April 20, 2020**. Positive month-end endpoints permit a log change but do not remove contract-roll and delivery effects. **Mitigated:** invalid endpoint tests, negative-price audit, dollar-change and crisis-window sensitivities; results remain proxy-based. V1's simple/log scenario conflation is corrected in new scenario outputs, with mean confidence intervals clearly distinguished from prediction intervals.
5. **P1 — Exploratory inference and predictive overreach.** Models were not preregistered and have no out-of-sample validation. **Mitigated:** common samples, HAC/HC3 uncertainty, familywise joint tests and full result tables. Structural identification and forecasting claims remain unsupported.

## Concrete next steps

1. Recover original April 2026 market downloads/environment and the GPR acquisition receipt, if available; compare hashes and reconcile the small replay differences. Do not overwrite either vintage.
2. Specify the economic estimand before changing oil inputs: oil spot-price exposure versus a tradable collateralized futures strategy. Obtain a documented contract/roll series and reconcile it with a separately sourced spot benchmark; do not call CL=F an investment return.
3. Compare the retained daily-mean GPR with the publisher's official monthly series as a separately dated sensitivity, not a silent substitution. Establish release timing/vintages before any predictive evaluation.
4. Freeze a small set of hypotheses and an untouched chronological holdout, then assess stability and incremental forecast performance against market/own-return baselines. The current data have already been inspected and cannot be relabeled an untouched holdout.
5. For a causal mechanism claim, design identification around defensible exogenous shocks/instruments or a justified event study with competing channels and timing. Adding lags or doing coefficient subtraction alone is insufficient.

Evidence: generated tables under `outputs/v2/`; definitions and primary-source links in [METHODOLOGY_V2.md](METHODOLOGY_V2.md). Tests and offline reruns support software correctness within the documented scope, not causal validity.

# Version 2 methodology and reproduction contract

Scope fixed on 2026-10-25 (America/Chicago). This is a retrospective, exploratory association study, not a trading model or causal mediation analysis. No random simulation is used in estimation. Synthetic tests use seed 20261025.

## Evidence and vintages

| Input | V1 evidence | V2 treatment |
|---|---|---|
| XLE | Retained monthly CSV; no daily source snapshot or version lock | Explicit Yahoo `Adj Close` for distribution/split-adjusted vendor return proxy; `Close` sensitivity |
| WTI | `CL=F` fetched without end date; original download absent | Explicit Yahoo `Close`; stitched front-contract price proxy, not a roll-adjusted futures investment return |
| S&P 500 | `^GSPC`, original download absent | Explicit Yahoo `Close`; price index return, excluding dividends |
| GPR | Retained daily workbook, 1985-01-01 to 2026-04-27; retrieval date unknown | Same workbook, hash recorded; calendar-day mean of `GPRD`, not asserted equivalent to the publisher's monthly GPR |

Market data are newly retrieved October 25 local / October 26 UTC, 2026. Exact UTC timestamps, yfinance version, arguments, SHA-256 and symbols are in `outputs/v2/manifest.json`. This current market vintage is combined with the retained GPR vintage transparently; it is not presented as a real-time information set. A provider history or adjustment revision can change results after a new download. Downloading the same date range does not recover the original vintage.

`auto_adjust=False`, `back_adjust=False`, `repair=False` and `actions=True` make the raw field choice explicit. Yahoo's adjusted close is a vendor proxy, not an independently reconstructed dividend-reinvestment series. Company rankings from V1 use unadjusted close and omit market controls; V2 does not promote those rankings.

The retained workbook identifies GPRD as “Daily GPR (Index: 1985:2019=100)” and N10D as article counts across ten recent newspapers. Its schema and definitions are consistent with the cited publisher, but there is no historical download receipt to authenticate the exact workbook vintage. The author's current landing page could not be fetched by the web reader (size limit); the primary replication page and paper were accessible. No new GPR vintage was substituted.

## Calendar, returns, and sample

1. Preserve original notebook, data and three output files byte-for-byte. SHA-256 checks appear in `v1_audit.json`; the old README is copied to `docs/v1/README.md`.
2. Run all 33 original code cells in a separate sandbox. Substitute cached Yahoo data ending April 28, 2026 and infer `auto_adjust=True` where omitted; this is a documented reconstruction. Tail-expression rich displays are not reproduced by `exec`; saved charts and printed summaries are regenerated. A normal notebook kernel execution against the original, missing downloads is not claimed.
3. Retain actual last valid trading date for each calendar month, then compute `log(P_t) - log(P_(t-1))`. Empty months are explicit, no forward fill, and lags are computed on the complete monthly calendar before dropping rows. GPR must have every calendar day; partial months are excluded.
4. V2 ends March 31, 2026. The workbook has only 27 April days, while V1's market data included April 28. Relabeling partial data as April 30 does not complete April. Market downloads contain full April only to support auditing; April is excluded from every V2 estimation.
5. CL=F begins August 23, 2000 in the fresh download. September 2000 is the first month-end price change. V1 reconstructed sample: September 2000–April 2026, 308 rows. Completed-month baseline: September 2000–March 2026, 307 rows. Shared sample across comparison specifications: October 2000–March 2026, 306 rows because one lag of the oil change is needed. Inclusion/missingness is recorded per month in `sample_ledger.csv`.
6. `endpoint_audit.csv` records calendar-day distance from month end and equity/oil date agreement. This is an observed endpoint audit, not a complete exchange-holiday verification. A future input with a long outage requires inspection before analytical promotion; the current panel's endpoints were checked.

Nonpositive price endpoints invalidate both adjacent log changes; they are never clipped, absolutized or replaced with an arbitrary epsilon. The negative daily WTI observation on April 20, 2020 is retained in a separate audit. March and April month-end endpoints are positive, so the monthly log change exists. This does not repair roll discontinuities, collateral costs or the economic interpretation of the continuous ticker. Sensitivities use monthly dollar changes (different units) and exclude March–June 2020 using HC3, without pretending a gapped sample is equally spaced for HAC.

## Estimation and inference

Baseline: XLE log return on intercept, GPR/100, oil-proxy log change and S&P 500 log return. GPR/100 is a fixed rescaling, not a sample-fitted normalization. One GPR coefficient unit means a 100-index-point difference. Returns are decimal log returns: 0.01 is one log percentage point, approximately a 1% simple return for small changes.

All eleven comparison specifications are in `SPECS`, estimated on the identical 306-row sample. They include GPR–oil with a market control; contemporaneous plus one/two GPR lags with market and own-return controls; lagged-only XLE and oil equations; log-GPR-change alternatives; adjusted versus close XLE; and dollar-change oil sensitivity. Contemporaneous controls can absorb shared shocks or condition on downstream variables. Coefficient changes when oil is included are not mediation estimates.

Primary uncertainty: Bartlett Newey–West HAC with six monthly lags, finite-sample n/(n-k) correction and t-reference intervals. HAC(3), HAC(12) and HC3 are reported as sensitivity choices, not selected by favorable significance. HAC rejects gaps in the retained calendar sample. Eleven HAC(6) joint GPR tests receive Holm familywise adjustment; individual coefficient p-values and other covariance/sensitivity p-values remain unadjusted exploratory results. These models were developed after viewing V1, not prospectively preregistered. No rejection is not evidence of a zero effect.

Residual diagnostics and Cook's distance/leverage are exported for follow-up; they do not validate identification or stability. Lagged regressors establish temporal ordering in the calendar only: unrecovered release vintages, endogeneity and common shocks still preclude causal or real-time predictive claims. There is no out-of-sample forecast evaluation.

## Scenarios

V1 treated simple-looking scenario inputs as log returns and multiplied predicted log returns by 100. V2 accepts simple input changes, converts with `log1p`, and converts fitted log outputs with `expm1`. GPR is held at the common-sample median for all five scenarios to separate the assumed oil/market changes. Outputs are transformed fitted conditional log returns, not estimates of expected arithmetic returns (Jensen's inequality) and not forecast probabilities. Intervals transform the HAC confidence interval for the conditional mean log return; they exclude residual, parameter-selection, input and structural uncertainty and are not prediction intervals.

## Reproduction

Python 3.14.4, dependencies in `requirements.txt` (exact direct pins). From repository root:

```sh
python -m venv .venv
# Activate .venv using your shell, then:
python -m pip install -r requirements.txt
python main.py --fetch
python -m pytest -q
python main.py
```

First fetch stores daily data and a checksum receipt in ignored `data/raw/v2/`. Subsequent runs are offline and reject a changed cache. To refresh, deliberately move BOTH cache and receipt elsewhere first; preserve the old manifest and outputs as a separate vintage. Raw downloads are not added to Git. For exact same-vintage replication use the delivered local evidence bundle; a new clone's fetch can differ. Numerical results are deterministic for a given cache/environment; replay console summaries contain execution date/time and are not byte-stable. Optional `requirements-notebook.txt` installs Jupyter for inspecting the preserved notebook; executing it directly can overwrite V1 outputs and fetch unbounded current data, so use `main.py` for reproduction.

## Primary references (accessed 2026-10-25 local)

- Caldara and Iacoviello, *Measuring Geopolitical Risk*, American Economic Review 112(4), 2022: https://www.matteoiacoviello.com/gpr_files/GPR_PAPER.pdf
- Author replication material: https://www.matteoiacoviello.com/gpr_replication.htm
- Data landing page (historical workbook receipt unavailable): https://www.matteoiacoviello.com/gpr.htm
- yfinance download arguments and inclusive start/exclusive end: https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html
- statsmodels robust covariance reference: https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html
- EIA, April 27, 2020, negative WTI futures and storage: https://www.eia.gov/todayinenergy/detail.php?id=43495

Use provider data subject to its terms; no redistribution rights or official-source status are inferred from availability through yfinance.

# Cushing spot exposure and monthly GPR reconciliation

November 2, 2026 (Chicago). This revision supersedes the October CL=F primary specification. The comparison uses the previously fixed 306 completed months from October 2000 through March 2026.

## Exposure and sources

The target is the conditional association between XLE monthly log returns and monthly log changes in the physical Cushing WTI spot price in USD per barrel. We take the last observed daily EIA RWTC quote in each calendar month, retain its observation date, enforce the existing four-calendar-day freshness screen, and difference adjacent positive log prices. This aligns the oil measurement with equity month-end returns. The EIA daily observation on April 20, 2020 was −$36.98 per barrel. Both month-end prices needed for the April log change were positive. CL=F remains a stitched futures-price sensitivity with unresolved roll mechanics. [EIA daily RWTC](https://www.eia.gov/dnav/pet/hist/RWTCD.htm)

XLE and S&P 500 use the retained October market cache. The primary GPR measure is the recent ten-newspaper series named GPR in the publisher's April 2026 release. Its last observation is March 2026. Month-start labels map to the corresponding calendar month end. The publisher describes the monthly measure in terms of monthly article shares. Equal weighting of daily index readings is a separate construction. [Publisher methods and archive index](https://www.matteoiacoviello.com/gpr.htm) · [April monthly workbook](https://github.com/iacoviel/iacoviel.github.io/blob/259210729676a533a1256b512ab47c41f52fe2f0/gpr_archive_files/data_gpr_export_202604.xls)

The April 27 publisher daily archive matches all 15,092 dates and GPRD values in the retained workbook. The file hashes differ. This verifies the series used in V1 while its original download receipt is still missing. The EIA workbook downloaded November 2 local time contains observations through October 27, 2026. The model applies its March cutoff before aggregation. The input receipts retain URLs, UTC download times and exact file hashes. These retrospective sources do not establish what a forecaster could observe at each historical month end. [April 27 daily workbook](https://github.com/iacoviel/iacoviel.github.io/blob/259210729676a533a1256b512ab47c41f52fe2f0/gpr_archive_files/data_gpr_daily_recent_20260427.xls) · [Run manifest](../outputs/v2/manifest.json)

## Matched regressions

Each row uses identical months, adjusted XLE returns, S&P 500 price returns, an intercept and six-lag Bartlett HAC inference. GPR is scaled per 100 index points. The eleven primary GPR tests retain their Holm adjustment. The four source combinations below are descriptive sensitivity comparisons.

| Oil | GPR | Oil coefficient | 95% interval | GPR p | R² |
|---|---|---:|---:|---:|---:|
| EIA spot | Publisher monthly | 0.32176 | 0.23505 to 0.40847 | 0.08875 | 0.59135 |
| CL=F | Publisher monthly | 0.32120 | 0.22856 to 0.41385 | 0.06836 | 0.58934 |
| EIA spot | Retained daily mean | 0.32141 | 0.23478 to 0.40804 | 0.08283 | 0.59124 |
| CL=F | Retained daily mean | 0.32084 | 0.22830 to 0.41337 | 0.06320 | 0.58923 |

The observed difference in oil slopes between the first two rows is 0.00056. This comparison does not test statistical equivalence. Requiring a shared trading date for all three markets gives a spot coefficient of 0.32317. The prior CL=F and daily-GPR specification reproduces the previous draft. [Full matched estimates](../outputs/v2/matched_proxy_comparisons.csv)

## GPR and inference

All 306 months have an official reading and complete calendar-day coverage. Correlation between the publisher monthly index and the daily arithmetic mean is 0.99871. The mean absolute difference is 1.77 points. The largest gap occurs in March 2026, when the official index is 297.27 and the daily mean is 323.48. The two archive dates and aggregation methods differ. The available evidence leaves the exact contribution of source revisions and aggregation to individual discrepancies unresolved. [Month-by-month reconciliation](../outputs/v2/gpr_reconciliation.csv)

In the primary model, a 100-point higher GPR is associated with 0.00732 higher fitted XLE log return, with a 95% interval of −0.00112 to 0.01575. The market-controlled GPR–spot test has p=0.787. The smallest Holm-adjusted p-value across the eleven joint GPR tests is 0.570. The evidence supports a positive contemporaneous oil-price association. Causal transmission and predictive performance remain unresolved. Residual serial dependence persists (Ljung–Box lag 12 p=0.015). Parameter stability, exchange-calendar reconciliation and a prospective forecasting evaluation remain open.

## Reproduction and validation

Run `python main.py --fetch --verify-repeat` after installing `requirements-lock.txt`. Subsequent runs use `python main.py --verify-repeat` offline. New source workbooks and receipts are stored under ignored `data/raw/spot_review/`. The EIA URL serves an updating workbook. The local revision bundle contains the exact downloaded bytes. The full eligible spot baseline has 321 observations, with calendar-HAC inference across gaps. Comparisons in this report all use the fixed 306-month sample.

The 35 local tests passed. Two offline runs matched all 13 CSV outputs after the declared line-ending normalization. The V1 replay executed all 33 cells. Primary models, scenarios, diagnostics and the common-date sensitivity all use spot prices and publisher monthly GPR. Historical October review documents refer to the preceding revision.

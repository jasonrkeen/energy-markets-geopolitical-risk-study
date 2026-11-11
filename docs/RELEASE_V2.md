# Version 2.0.0: XLE oil-price exposure

**November 11, 2026 | Status: merged retrospective exploratory study | Author: Jason Keen**

## Decision summary

This release supports an exploratory historical study of XLE's association with physical Cushing WTI spot prices. The positive oil association survives the reported source, period and crisis sensitivities. The full model does show evidence of changing coefficients, and residual serial dependence remains. It should not be described as a stable forecasting rule, a trading strategy, or evidence of causal GPR transmission through oil.

The primary specification uses 306 completed months, October 2000-March 2026. Conditional oil exposure is 0.32176 (95% HAC(6) interval 0.23505-0.40847). Approximately, a 1% higher monthly spot-price change is associated with 0.32% higher XLE return, holding market return and GPR fixed in the fitted model. This is a log-return approximation, not an investable oil return. R-squared is 0.59135 and measures in-sample fit.

## Inputs and methodological contract

- XLE uses retained Yahoo adjusted closes, a vendor distribution/split-adjustment proxy. S&P 500 uses price-index returns, excluding dividends. The new work does not claim a common total-return convention across the two series.
- Oil uses the last available daily EIA RWTC Cushing spot quote in each month, followed by adjacent-month log differences. CL=F is retained only as a stitched futures-price sensitivity with unresolved roll mechanics.
- GPR uses the publisher's recent ten-newspaper monthly index from the April 2026 archive, ending March 2026. The retained arithmetic average of daily GPR is a sensitivity.
- Actual quote dates are retained. Endpoints over four calendar days old and nonpositive endpoints invalidate adjacent log changes. There is no missing-value forward filling. April 2026 is excluded as incomplete in the original study.
- HAC(6) inference uses Bartlett weights, a finite-sample correction and t-based intervals. Existing HAC(3/12), HC3 and all eleven primary GPR joint tests remain available. Crisis exclusions use actual-calendar HAC, avoiding compression of omitted months.
- Sources are retrospective vintages. The EIA download was acquired November 2 local time and the market cache in October. These are not reconstructed real-time information sets.

[Source reconciliation and exact archive links](SPOT_GPR_RECONCILIATION.md), [manifest](../outputs/v2/manifest.json), [frozen review protocol](STABILITY_PROTOCOL.md).

## Stability review

The protocol was written before calculating these additional checks, after the baseline data and earlier sensitivities had already been inspected. The checks are exploratory, with no claim of preregistration or untouched holdout validation. All planned checks are retained.

| Specification | Months | Oil coefficient | 95% interval |
|---|---:|---:|---:|
| Full baseline | 306 | 0.32176 | 0.23505-0.40847 |
| October 2000-March 2009 | 102 | 0.29237 | 0.15107-0.43368 |
| April 2009-September 2017 | 102 | 0.30025 | 0.25045-0.35005 |
| October 2017-March 2026 | 102 | 0.31694 | 0.14337-0.49051 |
| Exclude September 2008-June 2009 | 296 | 0.33878 | 0.24225-0.43532 |
| Exclude March-June 2020 | 302 | 0.36513 | 0.28957-0.44069 |
| Exclude February-June 2022 | 301 | 0.31535 | 0.23128-0.39942 |
| Add one lagged XLE return | 306 | 0.35244 | 0.28630-0.41858 |

Seventeen overlapping 120-month rolling windows, stepped annually with the final window included, yield oil estimates from 0.21265 to 0.34819. These overlapping estimates are descriptive; their extrema are not a confidence interval.

A pooled model interacts the intercept and all regressors with the three period indicators. The robust equality test for the oil slopes has p=0.97611. The test that all coefficients are equal across periods has unadjusted p=0.02385 and Holm-adjusted p=0.04771 across the two stability tests. This is evidence against full-model constancy within the exploratory specification, with sensitivity to the chosen partitions and test family. It does not identify a change date or the particular coefficient driving the rejection. Non-rejection for oil alone does not establish stable exposure. The two stability tests are separate from the existing eleven-test GPR family; no study-wide familywise error guarantee is asserted.

The baseline Ljung-Box lag-12 residual test has p=0.01515. Adding one lagged XLE return raises R-squared to 0.61409, but the approximate lag-12 diagnostic, with one degree of freedom subtracted, still has p=0.02494. This diagnostic is approximate for a regression with external regressors. We do not select the dynamic model by these p-values or claim the remaining dependence has been fixed. HAC addresses estimated uncertainty under its assumptions, not omitted variables or unstable parameters.

[All estimates](../outputs/v2/stability_estimates.csv), [joint stability tests](../outputs/v2/stability_tests.csv), [diagnostics](../outputs/v2/stability_diagnostics.csv).

## Calendar and source review

Eighteen of the 306 months have different spot and equity endpoint dates. Maximum endpoint ages are four calendar days for spot and three for equities. The full month-by-month audit is retained. Requiring a shared available quote date gives an oil coefficient of 0.32317, compared with 0.32176 at separate month ends. These modest point-estimate differences do not establish statistical equivalence. The date audit is complete for the frozen sample, but does not independently verify every expected EIA release/trading date, explain each missing quote, or make intraday observation times synchronous. The four-day screen remains an empirical quality rule.

The April 20, 2020 daily spot quote was negative (-$36.98/barrel), but the relevant month-end endpoints are positive. Valid log differences of positive endpoints do not represent the daily path or an investable futures payoff.

The publisher daily archive matches all 15,092 retained GPRD values and dates, while file bytes differ. Official monthly GPR and the daily arithmetic mean correlate at 0.99871, with mean absolute difference 1.77 points and a March 2026 difference of 26.21 points. Different archive dates and aggregation methods prevent exact attribution of discrepancies to revisions versus aggregation. Original acquisition receipts are not recovered.

[Calendar audit](../outputs/v2/stability_calendar_audit.csv), [common-date sensitivity](../outputs/v2/common_date_sensitivity.json).

## GPR conclusion and red-team boundaries

Primary GPR p=0.08875, with its 95% coefficient interval spanning zero. The market-controlled GPR-spot test has p=0.78694. The smallest Holm-adjusted p among the eleven joint GPR tests is 0.57024. This evidence does not establish a zero effect, predictive value, or mediation through oil. Contemporaneous market controls may themselves lie on economic transmission paths; the reported estimand is a conditional association, not a total causal effect.

Remaining research limits are residual dependence, full-model instability, source-vintage differences, incomplete historical acquisition records, quote-calendar/timing uncertainty and the lack of a genuinely untouched predictive evaluation. They are disclosed limitations for a retrospective research release. They block stronger claims about causality, stable future exposure, precise historical V1 reproduction or investment performance.

## Validation and release contents

A new isolated Python 3.14.4 environment with system packages disabled installed requirements-lock.txt successfully; pip check found no broken requirements. A separate source copy and exact local raw caches passed 41 tests and two complete pipeline runs. All 17 numerical CSVs matched the development environment after declared CRLF-to-LF normalization. V1's 33 cells replayed and original-file fingerprints passed. The original 308-observation replay remains a near-reproduction, not the unavailable original market vintage.

An independent least-squares calculation verified the pooled interaction coefficients implied the separately fitted period coefficients to maximum absolute difference 2.31e-15. Validation is bounded to the same Windows machine and Python version; clean installation is not independent data acquisition or independent methodological review. Package installation reused downloaded wheel caches. No fresh source download was used for the numerical comparison.

Machine-readable environment, source and output checks are in [CLEAN_VALIDATION.json](CLEAN_VALIDATION.json). The executive PDF is built from the result tables using scripts/build_release.py and reportlab 4.4.9. The PDF is rendered and visually checked before delivery. The local reproduction bundle contains exact source bytes, code, tables, report, PDF and an integrity manifest. Raw data remain outside Git; redistribution or public archival requires checking source terms. Live Yahoo/EIA downloads can revise history, so exact replication uses the frozen bundle.

## Reproduce and review

1. Extract the supplied bundle to a new directory. Run `python scripts/verify_bundle.py` to verify BUNDLE_MANIFEST.json against the extracted bytes.
2. Create a Python 3.14 virtual environment and install requirements-lock.txt.
3. Run `python -m pytest -q`, then `python main.py --verify-repeat` using the included caches.
4. Compare the 17 CSV hashes with docs/CLEAN_VALIDATION.json using the declared line-ending normalization.
5. Optionally install requirements-report.txt and run `python scripts/build_release.py` to regenerate the executive PDF. PDF byte identity is not asserted because generated document metadata can vary.

PR #1 was marked ready and merged with owner authorization on November 11, 2026 (merge commit 7504e2b43f379635f11250f135bf4fea5ecda1ae). Main exactly matched the reviewed contents, and post-merge CI passed. Before forecasting, freeze hypotheses and a future evaluation window with release-time data. Before causal claims, establish a defensible identification design. Recovery of the original daily market downloads would strengthen V1 reproduction, but their absence is not concealed by the current-vintage numerical match.

## Final red-team disposition

[Final review](FINAL_RED_TEAM.md) found and fixed a silent sample-reduction path in the common-date sensitivity and a stale-narrative path in PDF generation. The fixed stability date window now rejects shifted samples. Independent synthetic calculations verify the robust pooled Wald tests. These safeguards do not change any of the 17 frozen numerical CSVs. The final 41-test rerun used another separate source copy and the previously created isolated environment; the environment was not recreated for this follow-up.

PDF generation now requires the numerical tables, common-date JSON and validated source hashes to match the frozen editorial inputs and current validation receipt. Changed data require renewed editorial review. No unresolved release-blocking defect was found for the declared retrospective scope. An external independent methodological review has not occurred; this is an agent self-review with independent numerical cross-checks.

## Sharing and archive scope

Version 2.0.0 is the final retrospective release. The public reproduction bundle contains repository code, derived tables, source manifests, the already tracked V1 artifacts, this report and the executive PDF. Newly acquired raw EIA, publisher and Yahoo caches are excluded from public assets because their redistribution review is incomplete. The separately retained local full-input archive includes the exact cached bytes and supports the documented offline replication.

For the public bundle, run `python main.py --fetch --verify-repeat` after dependency installation. A live fetch is a new-vintage replication attempt and may differ or fail a source/schema check; it is not guaranteed to recover the frozen estimates. The frozen executive PDF intentionally refuses to rebuild from changed numerical results until its narrative is reviewed. Existing tables and validation receipts remain available for inspection. The source-inclusive local bundle uses `python main.py --verify-repeat` without fetching.

The release tag identifies the publication commit. Asset checksums are provided in SHA256SUMS.txt. The 41-test validation and 17-table numerical equality apply to the reviewed analysis code, unchanged during publication. Historical October and candidate review records are retained with their original context.

## Distribution revision 2 supersedes the initial asset inventory

The [redistribution review](DATA_REDISTRIBUTION.md) now permits the publisher GPR snapshots under CC BY 4.0 with [attribution](DATA_ATTRIBUTION.md). Yahoo caches remain excluded; EIA RWTC redistribution remains unresolved because of third-party spot-price sourcing. The replacement public ZIP additionally omits extensive price/return histories and saved notebook evidence. It is a partial reproduction kit requiring authorized omitted inputs, not an offline runnable archive. Earlier reproduction instructions apply to the retained full local archive. The unchanged tag and generated GitHub source archives still expose earlier committed observations and are not certified as cleared by this review. No scientific result changed.

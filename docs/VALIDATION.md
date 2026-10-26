# Validation scope

**Share with caveats. Completeness: partial historical reproduction; implemented V2 association workflow.** Repairs were made on a branch. Totals below are scoped inventory counts, not an overall accuracy score; 0/N means no remaining demonstrated defect, not complete source authentication.

Inventory: four focal input series (XLE, CL=F, S&P 500, GPR); three consequential calculation groups (V1 replay, V2 model comparisons, scenarios); one new coefficient chart; three narrative claims (oil/market association, uncertain GPR association, no established mediation). V1 company/volatility/extreme-GPR analyses were code-replayed but not promoted as V2 claims. Interactive dashboard behavior is out of scope.

## Artifact quality

| Category | Observed defects | Assessment |
|---|---|---|
| Usefulness/completeness | 0 / 3 | Audit, controlled comparisons and report delivered. Historical provenance and predictive/causal extensions remain explicitly unresolved. |
| Analytical clarity | 0 / 3 | The three focal claims carry sample, proxy and inference qualifications. |
| Visual/interaction consistency | 0 / 1 | New coefficient plot visually inspected for labels, intervals and clipping; no interactive controls. Original charts preserved; their rendered fidelity was not independently certified. |

## Analytical correctness and robustness

| Category | Observed defects | Assessment |
|---|---|---|
| Source authority/confidence | 0 / 4 | Current vendor fields and retained workbook inspected; original-vintage authentication unavailable for all four inputs. No official exchange/issuer reconstruction claimed. |
| Value accuracy | 0 / 3 | Archived return identity and simple regression verified; full notebook replay approximate; OLS/HAC independently tested on synthetic data; scenario conversion tested. |
| Within-chart agreement | 0 / 1 | Chart uses exported common-sample HAC(6) coefficients and intervals; units differ and are labeled. |
| Complete source details | 0 / 4 | Known source choices, dates and hashes recorded; missing historical acquisition evidence explicitly marked unknown. |
| Cross-artifact consistency | 0 / 3 | README/report, coefficient chart/table and replay/archive comparisons reconciled. |
| Data-quality controls | 0 / 4 | Calendar grid, duplicate dates, GPR coverage, missing/nonpositive endpoints and actual source dates checked. Three oil/equity endpoint differences retained and tested. No complete exchange-holiday audit. |
| Conclusion support | 0 / 3 | Conditional associations reported; mechanism and zero-effect conclusions withdrawn. No forecast validation asserted. |

Focused validation: 16 tests passed in a fresh Python 3.14.4 environment; all 33 original code cells ran with documented cache substitution. V1 notebook/data/output checksums stayed unchanged. The new plot was visually inspected. Generated console logs include timestamps; deterministic numeric outputs are checked separately. GitHub CI status is reported at PR handoff rather than assumed here.

Prioritized unresolved problems and remedies are in [FINDINGS_V2.md](FINDINGS_V2.md). A passing software check does not authenticate a missing historical source or establish causality.

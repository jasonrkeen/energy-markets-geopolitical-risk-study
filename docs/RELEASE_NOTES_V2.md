# Version 2.0.0 - XLE oil-price exposure

Final retrospective exploratory study, covering 306 completed months from October 2000 through March 2026. PR #1 merged after review, 41 tests and passing post-merge checks. Publication updates do not change the estimation code or the 17 numerical result tables.

## Findings

- EIA Cushing WTI spot-price exposure: 0.32176; 95% HAC interval 0.23505-0.40847. Matched CL=F sensitivity: 0.32120.
- GPR coefficient p=0.08875; no supported causal mediation or forecasting claim.
- Full-model stability test: exploratory Holm-adjusted p=0.04771. Residual dependence remains.

## Assets and reproduction

The release includes the final report, two-page executive PDF, public reproduction ZIP, and SHA256SUMS.txt. The ZIP includes code, derived outputs, receipts and already tracked V1 artifacts. Newly acquired raw caches are omitted from public assets pending redistribution review. The local full-input archive retains the exact bytes used for the verified 17-table offline reproduction.

Public users can install requirements-lock.txt and run `python main.py --fetch --verify-repeat`. This is a current-vintage rerun, not guaranteed exact replication. EIA and Yahoo histories can revise, endpoints can fail availability/schema checks, and provider availability is outside this release's control. The supplied numerical tables and their hashes preserve the reviewed findings. The PDF builder refuses changed numerical inputs until the fixed narrative receives editorial review.

## Documented limitations

Results are conditional historical associations. They do not establish causal transmission, absence of a GPR effect, stable future exposure, investable futures returns, or out-of-sample predictive performance. Residual dependence, full-model instability, source-vintage differences, missing original market downloads, GPR aggregation/revision ambiguity, and incomplete calendar/intraday verification remain. V1 is a qualified near-reproduction. Clean-environment validation was on the same Windows machine; hosted CI covers tests. The final review was agent self-review with independent numerical cross-checks, not external peer review.

The final report provides all methods, sensitivity results, source dates and next research steps. Original V1 artifacts remain preserved. Release status does not remove the stated limitations.

## Distribution revision 2 - November 11, 2026

This addendum supersedes the original ZIP inventory and public-rerun instructions above. The replacement attached ZIP includes CC BY 4.0 publisher GPR snapshots with attribution, but excludes Yahoo data, the unresolved EIA/Refinitiv workbook and extensive row-level market outputs. It is a partial reproduction kit: omitted V1 evidence and authorized inputs are required for a full run or all preservation tests. See the attached data-redistribution.md and data-attribution.md. The unchanged Git tag and GitHub-generated source archives still contain earlier observations; those separate legacy exposures remain unresolved. The original local full-input archive is preserved. Source estimates and tag are unchanged.

# Final red-team review

November 11, 2026. Review baseline: d739736. Decision: **ready to merge as a retrospective exploratory study after the final checks pass**. Keep PR #1 draft and unmerged for the owner's decision.

## Supported findings and fixes

| Priority | Finding | Fix / evidence |
|---|---|---|
| P2 | The common-date comparison passed missing months to OLS, whose dropna could silently reduce the claimed matched sample. The frozen sample is complete, so existing results are unaffected. | Require every fixed comparison month and finite inputs before fitting. Regression coverage rejects missing months and infinity. |
| P2 | PDF generation checked only a success flag and test count. Updated tables could be combined with hard-coded historical prose, and Python optimization could disable the assert. | Explicit exceptions enforce exact normalized hashes for all 17 CSVs, the common-date JSON, and validated source files. A separate frozen editorial input manifest prevents blindly refreshing the validation receipt from authorizing stale prose. Tests cover altered tables, refreshed receipts and changed source. |
| P3 | Stability-window validation accepted any consecutive 306 months, although its interpretation is tied to October 2000-March 2026. | Require the exact month-end index. Regression coverage rejects a shifted 306-month window. |

## Methodological checks

- Rechecked source provenance, adjustment conventions, complete-month and negative-price treatment, month-end date mismatch disclosure, same-sample comparisons, lag creation before row exclusion and calendar-distance HAC for crisis gaps.
- Verified pooled interaction tests independently using least squares, directly constructed Bartlett covariance, and F-tail probabilities on deterministic synthetic data. Restrictions test two oil-slope differences and eight full-coefficient differences. Both match the implementation to relative tolerance 1e-10.
- All planned stability checks remain reported. The borderline full-model result is explicitly exploratory and conditional on period boundaries and the two-test family. It is not a study-wide error-control guarantee or proof of an economic regime change.
- The lagged-return model is a sensitivity, not a selected replacement. Its Ljung-Box approximation is labeled. Residual dependence and instability are retained as limitations.
- Report claims distinguish in-sample associations from forecasting, causal mediation and investment returns. GPR non-rejection is not presented as proof of no effect. Revised sources do not authenticate missing original acquisition vintages.
- The raw source-inclusive bundle remains local. Git retains code, derived outputs, source receipts and download instructions. Public archiving of the exact raw bundle remains subject to source terms. Fresh live downloads can differ from the frozen results.

## Validation and scope

41 tests passed in development and in another separate source copy using the isolated environment created during release-candidate validation. Both pipeline runs repeated all 17 numerical CSVs identically. Cross-environment hashes and the prior candidate's CSV hashes agree. Source/output integrity checks and V1 frozen-file checks pass. Final CI results are reported on PR #1. The refreshed executive PDF is rendered and inspected before delivery.

This is a final agent self-review, with independent numerical cross-checks, not an external referee review. Same-machine environment isolation does not establish cross-platform full-pipeline validation; hosted CI covers tests only.

## Merge recommendation and remaining boundaries

No unresolved P1/P2 issue was found that blocks merging the declared retrospective study after these fixes and checks. The oil association is a qualified historical average. Residual dependence, full-model instability, calendar/intraday uncertainty, GPR revision/aggregation differences, and unavailable original market downloads remain explicit limitations. They block stronger causal, stable-exposure, exact historical-vintage or forecasting claims, rather than this bounded retrospective release.

No merge or ready-for-review transition is performed. Owner approval remains the next release action. An untouched future evaluation and a suitable causal design are separate research projects, not implied by merge readiness.

"""Fixed exploratory stability checks; protocol in docs/STABILITY_PROTOCOL.md."""
from pathlib import Path
import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.multitest import multipletests
from src.v2_models import fit

REGRESSORS = ["gpr100", "oil", "market"]
WINDOW = 120
STEP = 12
CRISES = (("exclude_gfc", "2008-09", "2009-06"),
          ("exclude_covid", "2020-03", "2020-06"),
          ("exclude_2022", "2022-02", "2022-06"))


def period_labels(index: pd.DatetimeIndex) -> np.ndarray:
    expected = pd.date_range("2000-10-31", "2026-03-31", freq="ME")
    if not index.equals(expected):
        raise ValueError("Stability review requires the fixed 306 consecutive months")
    return np.repeat(np.arange(3), 102)


def rolling_starts(n: int) -> list[int]:
    if n < WINDOW:
        raise ValueError("Insufficient rolling window")
    return sorted(set([*range(0, n - WINDOW + 1, STEP), n - WINDOW]))


def review(common: pd.DataFrame, out: Path) -> None:
    labels = period_labels(common.index)
    if common[["xle", *REGRESSORS, "xle_lag1"]].isna().any().any():
        raise ValueError("Stability inputs incomplete")
    rows = []

    def record(name: str, frame: pd.DataFrame, xs: list[str], cov: str = "HAC6"):
        result = fit(frame, "xle", xs, cov)
        for term in result.params.index:
            ci = result.conf_int().loc[term]
            rows.append(dict(model=name, term=term, beta=result.params[term],
                ci_low=ci.iloc[0], ci_high=ci.iloc[1], p=result.pvalues[term],
                n=int(result.nobs), start=str(frame.index[0].date()), end=str(frame.index[-1].date()),
                covariance=cov, r_squared=result.rsquared))
        return result

    baseline = record("baseline", common, REGRESSORS)
    for i in range(3):
        record(f"period_{i+1}", common.loc[labels == i], REGRESSORS)
    for start in rolling_starts(len(common)):
        record(f"rolling_{start:03d}", common.iloc[start:start+WINDOW], REGRESSORS)
    for name, first, last in CRISES:
        months = common.index.to_period("M")
        record(name, common.loc[~months.isin(pd.period_range(first, last, freq="M"))],
               REGRESSORS, "calendarHAC6")
    dynamic = record("lagged_xle", common, [*REGRESSORS, "xle_lag1"])
    pd.DataFrame(rows).to_csv(out / "stability_estimates.csv", index=False)

    pooled = common.copy()
    interactions = []
    for i in (1, 2):
        indicator = (labels == i).astype(float)
        for term in ["const", *REGRESSORS]:
            name = f"period{i+1}_{term}"
            pooled[name] = indicator * (1 if term == "const" else pooled[term])
            interactions.append(name)
    result = fit(pooled, "xle", [*REGRESSORS, *interactions])
    tests = []
    for name, terms in [("equal_oil_slopes", [t for t in interactions if t.endswith("_oil")]),
                        ("equal_all_coefficients", interactions)]:
        restriction = np.zeros((len(terms), len(result.params)))
        for i, term in enumerate(terms):
            restriction[i, result.params.index.get_loc(term)] = 1
        tests.append(dict(test=name, restrictions=len(terms),
                          p=float(result.wald_test(restriction, scalar=True).pvalue)))
    tests = pd.DataFrame(tests)
    tests["p_holm_two_stability_tests"] = multipletests(tests.p, method="holm")[1]
    tests.to_csv(out / "stability_tests.csv", index=False)
    diagnostics = []
    for name, result, df in [("baseline", baseline, 0), ("lagged_xle", dynamic, 1)]:
        lb = acorr_ljungbox(result.resid, lags=[12], model_df=df, return_df=True).iloc[0]
        diagnostics.append(dict(model=name, lag=12, diagnostic_df_adjustment=df,
                                ljung_box=lb.lb_stat, p=lb.lb_pvalue, n=int(result.nobs)))
    pd.DataFrame(diagnostics).to_csv(out / "stability_diagnostics.csv", index=False)
    audit = common[["xle_date", "oil_date", "market_date"]].copy()
    for name in ["xle", "oil", "market"]:
        audit[name + "_age_days"] = (audit.index.to_series() - audit[name + "_date"]).dt.days
    audit["same_date"] = (audit.xle_date == audit.oil_date) & (audit.xle_date == audit.market_date)
    audit.to_csv(out / "stability_calendar_audit.csv")

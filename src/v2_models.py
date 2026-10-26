"""Exploratory associations; no mediation or causal identification."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from src.config import CONFIG

def calendar_hac_covariance(design: np.ndarray, residuals: np.ndarray,
                            dates: pd.DatetimeIndex, maxlags: int) -> np.ndarray:
    """Bartlett sandwich over actual calendar lags; omitted months contribute zero scores.

    No observations are imputed and n/(n-k) uses observed n, not grid length.
    On a contiguous monthly sample this equals the usual corrected Newey-West estimate.
    """
    months = dates.to_period("M").asi8
    if len(months) != len(design) or not np.all(np.diff(months) > 0) or maxlags < 0:
        raise ValueError("Calendar HAC needs sorted unique months and nonnegative bandwidth")
    scores = np.zeros((months[-1] - months[0] + 1, design.shape[1]))
    scores[months - months[0]] = design * residuals[:, None]
    meat = scores.T @ scores
    for lag in range(1, min(maxlags + 1, len(scores))):
        cross = scores[lag:].T @ scores[:-lag]
        meat += (1 - lag/(maxlags + 1)) * (cross + cross.T)
    bread = np.linalg.inv(design.T @ design)
    n, k = design.shape
    return bread @ meat @ bread * n/(n-k)

SPECS = {
    "xle_gpr_market": ("xle", ["gpr100", "market"]),
    "xle_full": ("xle", ["gpr100", "oil", "market"]),
    "oil_gpr_market": ("oil", ["gpr100", "market"]),
    "oil_gpr_lags_controlled": ("oil", ["gpr100", "gpr100_lag1", "gpr100_lag2", "market", "oil_lag1"]),
    "xle_gpr_lags_controlled": ("xle", ["gpr100", "gpr100_lag1", "gpr100_lag2", "oil", "market", "xle_lag1"]),
    "oil_lagged_only": ("oil", ["gpr100_lag1", "gpr100_lag2", "oil_lag1", "market_lag1"]),
    "xle_lagged_only": ("xle", ["gpr100_lag1", "gpr100_lag2", "xle_lag1", "oil_lag1", "market_lag1"]),
    "xle_gpr_change": ("xle", ["dgpr", "oil", "market"]),
    "oil_gpr_change": ("oil", ["dgpr", "market"]),
    "xle_close_sensitivity": ("xle_price", ["gpr100", "oil", "market"]),
    "xle_oil_dollar_sensitivity": ("xle", ["gpr100", "oil_dollars", "market"]),
}

def fit(frame: pd.DataFrame, y: str, xs: list[str], covariance: str = "HAC6"):
    if not isinstance(frame.index, pd.DatetimeIndex) or frame.index.hasnans or not frame.index.is_monotonic_increasing:
        raise ValueError("Model dates must be sorted nonmissing timestamps")
    if frame.index.to_period("M").has_duplicates or not frame.index.is_month_end.all():
        raise ValueError("Model dates must be unique calendar month ends")
    sample = frame[[y] + xs].dropna()
    if len(sample) <= len(xs) + 2 or not np.isfinite(sample.to_numpy()).all():
        raise ValueError("Insufficient or nonfinite model sample")
    design = sm.add_constant(sample[xs], has_constant="add")
    if np.linalg.matrix_rank(design) != design.shape[1]:
        raise ValueError("Rank-deficient design")
    model = sm.OLS(sample[y], design, missing="raise")
    if covariance.startswith("calendarHAC"):
        bandwidth = int(covariance.removeprefix("calendarHAC"))
        result = model.fit(cov_type="HAC", cov_kwds={"maxlags": bandwidth,
                           "kernel": "bartlett", "use_correction": True}, use_t=True)
        # Set the underlying result before any cached bse/pvalues/interval properties are read.
        result._results.cov_params_default = calendar_hac_covariance(
            design.to_numpy(), result.resid.to_numpy(), sample.index, bandwidth)
        result._results.cov_type = "calendarHAC"
        result._results.cov_kwds["description"] = "Bartlett HAC using actual calendar-month lag distances"
        return result
    if covariance.startswith("HAC"):
        months = sample.index.to_period("M").asi8
        if not np.all(np.diff(months) == 1):
            raise ValueError("HAC requires consecutive calendar months; use HC3 for gaps")
        return model.fit(cov_type="HAC", cov_kwds={"maxlags": int(covariance[3:]),
                         "kernel": "bartlett", "use_correction": True}, use_t=True)
    if covariance == "HC3":
        return model.fit(cov_type="HC3", use_t=True)
    if covariance == "nonrobust":
        return model.fit()
    raise ValueError("Unknown covariance")

def estimate(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    required = sorted(set(c for y, xs in SPECS.values() for c in [y] + xs))
    expected = pd.date_range(CONFIG.comparison_start, CONFIG.complete_through, freq="ME")
    common = panel.reindex(expected)[required]
    if common.isna().any().any():
        missing = common.index[common.isna().any(axis=1)].strftime("%Y-%m").tolist()
        raise ValueError(f"Fixed comparison sample incomplete; inspect inputs: {missing}")
    ledger = panel[required].isna().rename(columns=lambda c: "missing_" + c)
    ledger["included_common"] = panel.index.isin(common.index)
    ledger["outside_fixed_comparison_window"] = ~panel.index.isin(expected)
    rows, tests = [], []
    for name, (y, xs) in SPECS.items():
        for cov in ["HC3"] + [f"HAC{k}" for k in CONFIG.hac_lags]:
            result = fit(common, y, xs, cov)
            ci = result.conf_int()
            for term in result.params.index:
                rows.append(dict(model=name, covariance=cov, term=term,
                    coefficient=result.params[term], se=result.bse[term], p=result.pvalues[term],
                    ci_low=ci.loc[term, 0], ci_high=ci.loc[term, 1], n=int(result.nobs),
                    start=str(common.index.min().date()), end=str(common.index.max().date()),
                    r_squared=result.rsquared))
            if cov == "HAC6":
                terms = [x for x in xs if "gpr" in x]
                restriction = np.zeros((len(terms), len(result.params)))
                for i, term in enumerate(terms):
                    restriction[i, result.params.index.get_loc(term)] = 1
                tests.append(dict(model=name, hypothesis="all GPR terms jointly zero",
                                  p=float(result.wald_test(restriction, scalar=True).pvalue)))
    joint = pd.DataFrame(tests)
    joint["p_holm_across_models"] = multipletests(joint.p, method="holm")[1]
    # Preserve HC3 as a contrast, but also address residual dependence across actual calendar lags.
    reduced = common.loc[~common.index.to_period("M").isin(pd.period_range("2020-03", "2020-06", freq="M"))]
    for cov in ["HC3", "calendarHAC6"]:
        r = fit(reduced, "xle", ["gpr100", "oil", "market"], cov)
        ci = r.conf_int()
        for term in r.params.index:
            rows.append(dict(model="xle_exclude_mar_jun2020", covariance=cov, term=term,
                coefficient=r.params[term], se=r.bse[term], p=r.pvalues[term],
                ci_low=ci.loc[term, 0], ci_high=ci.loc[term, 1], n=int(r.nobs),
                start=str(reduced.index.min().date()), end=str(reduced.index.max().date()), r_squared=r.rsquared))
    return pd.DataFrame(rows), joint, ledger

def scenario_log_prediction(params: pd.Series, gpr100: float, oil_simple: float, market_simple: float) -> float:
    if not np.isfinite([gpr100, oil_simple, market_simple, *params]).all():
        raise ValueError("Scenario inputs and coefficients must be finite")
    if oil_simple <= -1 or market_simple <= -1:
        raise ValueError("Simple returns must exceed -100%")
    log_prediction = (params["const"] + params["gpr100"] * gpr100 +
                      params["oil"] * np.log1p(oil_simple) + params["market"] * np.log1p(market_simple))
    return float(np.expm1(log_prediction))

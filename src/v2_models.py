"""Exploratory associations; no mediation or causal identification."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from src.config import CONFIG

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
    sample = frame[[y] + xs].dropna()
    if len(sample) <= len(xs) + 2 or not np.isfinite(sample.to_numpy()).all():
        raise ValueError("Insufficient or nonfinite model sample")
    design = sm.add_constant(sample[xs], has_constant="add")
    if np.linalg.matrix_rank(design) != design.shape[1]:
        raise ValueError("Rank-deficient design")
    model = sm.OLS(sample[y], design, missing="raise")
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
    common = panel.dropna(subset=required)
    ledger = panel[required].isna().rename(columns=lambda c: "missing_" + c)
    ledger["included_common"] = panel.index.isin(common.index)
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
    # Pandemic sensitivity uses HC3 because removing months introduces a calendar gap.
    reduced = common.loc[~common.index.to_period("M").isin(pd.period_range("2020-03", "2020-06", freq="M"))]
    r = fit(reduced, "xle", ["gpr100", "oil", "market"], "HC3")
    ci = r.conf_int()
    for term in r.params.index:
        rows.append(dict(model="xle_exclude_mar_jun2020", covariance="HC3", term=term,
            coefficient=r.params[term], se=r.bse[term], p=r.pvalues[term],
            ci_low=ci.loc[term, 0], ci_high=ci.loc[term, 1], n=int(r.nobs),
            start=str(reduced.index.min().date()), end=str(reduced.index.max().date()), r_squared=r.rsquared))
    return pd.DataFrame(rows), joint, ledger

def scenario_log_prediction(params: pd.Series, gpr100: float, oil_simple: float, market_simple: float) -> float:
    if oil_simple <= -1 or market_simple <= -1:
        raise ValueError("Simple returns must exceed -100%")
    log_prediction = (params["const"] + params["gpr100"] * gpr100 +
                      params["oil"] * np.log1p(oil_simple) + params["market"] * np.log1p(market_simple))
    return float(np.expm1(log_prediction))

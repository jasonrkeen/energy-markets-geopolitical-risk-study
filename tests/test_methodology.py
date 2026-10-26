"""Synthetic boundary tests; no network calls."""
import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose
from src.v2_data import log_returns, monthly_prices, monthly_gpr, validate_dates
from src.v2_models import fit, scenario_log_prediction

def test_returns_compound_and_invert():
    actual = log_returns(pd.Series([100., 110., 99.]))
    assert_allclose(np.expm1(actual.iloc[1:]), [.1, -.1])
    assert_allclose(np.expm1(actual.sum()), -.01)

@pytest.mark.parametrize("bad", [0., -37.63, np.nan])
def test_invalid_endpoint_invalidates_both_adjacent_returns(bad):
    assert log_returns(pd.Series([100., bad, 120.])).iloc[1:].isna().all()

def test_missing_month_is_not_bridged():
    daily = pd.Series([100., 120.], index=pd.to_datetime(["2024-01-31", "2024-03-28"]))
    result = monthly_prices(daily)
    assert len(result) == 3
    assert result["return"].isna().all()
    assert result.loc["2024-03-31", "source_date"] == pd.Timestamp("2024-03-28")

def test_negative_daily_oil_is_not_a_negative_month_end():
    daily = pd.Series([20., -37.63, 18.], index=pd.to_datetime(["2020-03-31", "2020-04-20", "2020-04-30"]))
    assert_allclose(monthly_prices(daily)["return"].iloc[-1], np.log(18/20))

def test_gpr_calendar_coverage_catches_partial_month_and_leap_day():
    result = monthly_gpr(pd.Series(100., index=pd.date_range("2024-02-01", "2024-03-27")))
    assert result.loc["2024-02-29", "complete"]
    assert result.loc["2024-02-29", "days_expected"] == 29
    assert not result.loc["2024-03-31", "complete"]

@pytest.mark.parametrize("dates", [["2024-01-01", "2024-01-01"], ["2024-02-01", "2024-01-01"]])
def test_duplicate_or_unsorted_dates_rejected(dates):
    with pytest.raises(ValueError):
        validate_dates(pd.to_datetime(dates))

def sample():
    rng = np.random.default_rng(20261025)
    x = rng.normal(size=80)
    return pd.DataFrame({"x": x, "y": 1 + 2*x + rng.normal(size=80)},
                        index=pd.date_range("2010-01-31", periods=80, freq="ME"))

def test_ols_against_independent_lstsq_and_hac_against_sandwich():
    data = sample()
    model = fit(data, "y", ["x"], "HAC3")
    design = np.column_stack([np.ones(len(data)), data.x])
    beta = np.linalg.lstsq(design, data.y, rcond=None)[0]
    assert_allclose(model.params, beta)
    scores = design * (data.y.to_numpy() - design @ beta)[:, None]
    meat = scores.T @ scores
    for lag in range(1, 4):
        cross = scores[lag:].T @ scores[:-lag]
        meat += (1 - lag/4) * (cross + cross.T)
    bread = np.linalg.inv(design.T @ design)
    assert_allclose(model.cov_params(), bread @ meat @ bread * len(data)/(len(data)-2), rtol=1e-10)

def test_hac_rejects_calendar_gaps_but_hc3_allows_them():
    data = sample().drop(pd.Timestamp("2011-01-31"))
    with pytest.raises(ValueError, match="consecutive"):
        fit(data, "y", ["x"], "HAC6")
    assert fit(data, "y", ["x"], "HC3").nobs == 79

def test_rank_deficient_model_is_rejected():
    with pytest.raises(ValueError, match="Rank"):
        fit(sample().assign(z=lambda x: x.x), "y", ["x", "z"])

def test_scenario_simple_return_conversion_is_exact_for_unit_beta():
    params = pd.Series({"const": 0., "gpr100": 0., "oil": 1., "market": 0.})
    assert_allclose(scenario_log_prediction(params, 1., -.1, 0.), -.1)
    with pytest.raises(ValueError):
        scenario_log_prediction(params, 1., -1., 0.)

def test_lags_on_calendar_grid_do_not_cross_missing_months():
    values = pd.Series([1., np.nan, 3.], index=pd.date_range("2024-01-31", periods=3, freq="ME"))
    assert pd.isna(values.shift(1).iloc[2])

def test_nonfinite_prices_rejected():
    with pytest.raises(ValueError):
        log_returns(pd.Series([1., np.inf]))

def test_common_date_sensitivity_uses_shared_trading_date():
    from src.v2_data import common_date_returns
    dates = pd.to_datetime(["2024-01-31", "2024-02-28", "2024-02-29"])
    frame = pd.DataFrame({("Adj Close", "XLE"): [100., 110., 121.],
                          ("Close", "CL=F"): [50., 55., np.nan],
                          ("Close", "^GSPC"): [1000., 1100., 1210.]}, index=dates)
    assert_allclose(common_date_returns(frame).iloc[-1], np.log(1.1))

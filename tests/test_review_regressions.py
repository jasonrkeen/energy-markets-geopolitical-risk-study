"""Regression tests for PR #1 review findings; synthetic inputs only except frozen-file integrity."""
import json
import shutil
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from src import v2_data as data
from src import v2_models as models
from src.config import ROOT
from src.run_artifacts import staged_output
from src.v1_audit import verify_frozen_inputs

def write_cache(tmp_path, monkeypatch):
    path = tmp_path / "market.csv"
    monkeypatch.setattr(data, "CACHE", path)
    cols = pd.MultiIndex.from_product([["Adj Close", "Close", "Open", "High", "Low"], data.CONFIG.tickers])
    frame = pd.DataFrame(100., index=pd.to_datetime(["2026-03-30", "2026-03-31"]), columns=cols)
    frame.to_csv(path)
    receipt = {"start": data.CONFIG.start, "end_exclusive": data.CONFIG.end_exclusive,
               "tickers": list(data.CONFIG.tickers), "auto_adjust": False, "back_adjust": False,
               "repair": False, "actions": True, "keepna": True, "sha256": data.sha256(path)}
    path.with_suffix(".json").write_text(json.dumps(receipt))
    return path, receipt

@pytest.mark.parametrize("key,value", [("auto_adjust", True), ("start", "2020-01-01"), ("tickers", ["XLE"])])
def test_cache_contract_rejected_even_with_valid_hash(tmp_path, monkeypatch, key, value):
    path, receipt = write_cache(tmp_path, monkeypatch)
    receipt[key] = value
    path.with_suffix(".json").write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="receipt/config mismatch"):
        data.read_market()

def test_cache_tamper_rejected(tmp_path, monkeypatch):
    path, _ = write_cache(tmp_path, monkeypatch)
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="checksum"):
        data.read_market()

def test_missing_required_field_rejected_even_if_hash_updated(tmp_path, monkeypatch):
    path, receipt = write_cache(tmp_path, monkeypatch)
    frame = pd.read_csv(path, header=[0, 1], index_col=0)
    frame.drop(columns=[("Adj Close", "XLE")]).to_csv(path)
    receipt["sha256"] = data.sha256(path)
    path.with_suffix(".json").write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="Missing market field"):
        data.read_market()

def test_orphaned_cache_not_overwritten(tmp_path, monkeypatch):
    path = tmp_path / "market.csv"
    path.write_text("irreplaceable input")
    monkeypatch.setattr(data, "CACHE", path)
    with pytest.raises(ValueError, match="Orphaned"):
        data.fetch()
    assert path.read_text() == "irreplaceable input"

def test_artifact_hash_is_portable_but_detects_changed_values(tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    a.write_bytes(b"value\r\n1\r\n")
    b.write_bytes(b"value\n1\n")
    assert data.content_hash(a) == data.content_hash(b)
    assert data.sha256(a) != data.sha256(b)
    b.write_bytes(b"value\n2\n")
    assert data.content_hash(a) != data.content_hash(b)

def test_stale_endpoint_invalidates_both_returns():
    prices = pd.Series([100., 101., 102.], index=pd.to_datetime(["2024-01-31", "2024-02-15", "2024-03-28"]))
    monthly = data.monthly_prices(prices)
    assert monthly.loc["2024-02-29", "stale_endpoint"]
    assert monthly["return"].isna().all()
    assert monthly.loc["2024-02-29", "observed_price"] == 101.

def test_intraday_duplicate_day_cannot_fake_gpr_coverage():
    dates = pd.date_range("2024-01-01", "2024-01-30").append(pd.DatetimeIndex(["2024-01-30 12:00"]))
    with pytest.raises(ValueError, match="midnight"):
        data.monthly_gpr(pd.Series(100., index=dates))

def regression_data():
    rng = np.random.default_rng(20261026)
    frame = pd.DataFrame(rng.normal(size=(80, 2)), columns=["x", "y"],
                         index=pd.date_range("2010-01-31", periods=80, freq="ME"))
    frame.y += 2 * frame.x
    return frame

def test_calendar_hac_matches_standard_hac_without_gaps():
    frame = regression_data()
    a = models.fit(frame, "y", ["x"], "HAC6")
    b = models.fit(frame, "y", ["x"], "calendarHAC6")
    assert_allclose(a.cov_params(), b.cov_params(), rtol=1e-12)
    assert_allclose(a.pvalues, b.pvalues, rtol=1e-12)
    assert_allclose(a.conf_int(), b.conf_int(), rtol=1e-12)

def test_calendar_hac_gap_matches_independent_pairwise_formula():
    frame = regression_data().drop(pd.date_range("2012-03-31", periods=4, freq="ME"))
    result = models.fit(frame, "y", ["x"], "calendarHAC6")
    x = np.column_stack([np.ones(len(frame)), frame.x])
    beta = np.linalg.lstsq(x, frame.y, rcond=None)[0]
    scores = x * (frame.y.to_numpy() - x @ beta)[:, None]
    meat = np.zeros((2, 2))
    months = frame.index.to_period("M").asi8
    for i in range(len(frame)):
        for j in range(len(frame)):
            distance = abs(months[i] - months[j])
            if distance <= 6:
                meat += (1 - distance/7) * np.outer(scores[i], scores[j])
    bread = np.linalg.inv(x.T @ x)
    assert_allclose(result.cov_params(), bread @ meat @ bread * len(frame)/(len(frame)-2), rtol=1e-12)
    compressed = frame.copy()
    compressed.index = pd.date_range("2010-01-31", periods=len(frame), freq="ME")
    assert not np.allclose(result.cov_params(), models.fit(compressed, "y", ["x"], "HAC6").cov_params())

def test_model_rejects_duplicate_months_for_hc3():
    frame = regression_data()
    frame.index = pd.DatetimeIndex([frame.index[0], *frame.index[:-1]])
    with pytest.raises(ValueError, match="unique"):
        models.fit(frame, "y", ["x"], "HC3")

def test_frozen_files_match_and_alteration_before_run_fails(tmp_path):
    frozen = verify_frozen_inputs()
    paths = ["docs/v1/FROZEN_INPUTS.json", *frozen["files"]]
    for name in paths:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    path = tmp_path / "data/processed/xle_monthly.csv"
    path.write_bytes(path.read_bytes() + b"altered before run")
    with pytest.raises(ValueError, match="Frozen V1"):
        verify_frozen_inputs(tmp_path)

def test_failed_run_leaves_prior_artifacts_and_success_retains_backup(tmp_path):
    destination = tmp_path / "v2"
    destination.mkdir()
    (destination / "old.csv").write_text("old evidence")
    with pytest.raises(RuntimeError):
        with staged_output(destination) as stage:
            (stage / "new.csv").write_text("incomplete")
            raise RuntimeError("model failed")
    assert (destination / "old.csv").read_text() == "old evidence"
    assert not (destination / "new.csv").exists()
    with staged_output(destination) as stage:
        (stage / "new.csv").write_text("completed")
    assert (destination / "new.csv").read_text() == "completed"
    assert len(list(tmp_path.glob(".v2-previous-*/old.csv"))) == 1

def test_daily_panel_to_models_and_fixed_sample_guard(monkeypatch):
    rng = np.random.default_rng(1001)
    dates = pd.bdate_range("2000-01-01", "2004-12-31")
    cols = pd.MultiIndex.from_tuples([("Adj Close", "XLE"), ("Close", "XLE"), ("Close", "CL=F"), ("Close", "^GSPC")])
    market = pd.DataFrame(100*np.exp(np.cumsum(rng.normal(0, .01, (len(dates), 4)), axis=0)), index=dates, columns=cols)
    calendar = pd.date_range("2000-01-01", "2004-12-31")
    gpr = pd.Series(rng.uniform(50, 200, len(calendar)), index=calendar)
    monkeypatch.setattr(data, "read_gpr", lambda: gpr)
    config = replace(data.CONFIG, start="2000-01-01", comparison_start="2000-10-31", complete_through="2004-12-31")
    monkeypatch.setattr(data, "CONFIG", config)
    monkeypatch.setattr(models, "CONFIG", config)
    panel, _ = data.build_panel(market)
    coefficients, tests, ledger = models.estimate(panel)
    assert ledger.included_common.sum() == 51
    assert len(tests) == 11
    assert set(coefficients.n) == {51}  # pandemic exclusion is outside this synthetic interval
    panel.loc["2004-12-31", "oil"] = np.nan
    with pytest.raises(ValueError, match="Fixed comparison sample incomplete"):
        models.estimate(panel)

@pytest.mark.parametrize("bad", [np.nan, np.inf])
def test_scenario_nonfinite_rejected(bad):
    params = pd.Series({"const": 0., "gpr100": 0., "oil": 1., "market": 0.})
    with pytest.raises(ValueError, match="finite"):
        models.scenario_log_prediction(params, 1., bad, 0.)

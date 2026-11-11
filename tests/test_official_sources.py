import numpy as np
import pandas as pd
import pytest

from src import v2_data
from src.official_sources import reconciliation


def test_official_series_supply_primary_changes_lags_and_risk(monkeypatch):
    dates = pd.date_range("2000-05-31", periods=5, freq="ME")
    market = pd.DataFrame({("Adj Close", "XLE"): [10, 12, 9, 10, 11],
                           ("Close", "XLE"): [10, 12, 9, 10, 11],
                           ("Close", "CL=F"): [20, 20, 25, 30, 35],
                           ("Close", "^GSPC"): [80, 85, 75, 81, 86]}, index=dates)
    spot = pd.Series([18, 19, 20, 22, 24], index=dates)
    official = pd.Series([90, 95, 100, 110, 120], index=dates)
    daily = pd.Series(200., index=pd.date_range("2000-05-01", dates[-1]))
    monkeypatch.setattr(v2_data, "read_gpr", lambda: daily)
    panel, _ = v2_data.build_panel(market, spot, official)
    row = panel.loc[dates[-1]]
    assert row.oil == pytest.approx(np.log(24/22))
    assert row.oil_lag1 == pytest.approx(np.log(22/20))
    assert row.futures == pytest.approx(np.log(35/30))
    assert row.oil_dollars == 2
    assert row.gpr100 == 1.2 and row.daily_gpr100 == 2
    assert row.gpr100_lag1 == 1.1


def test_reconciliation_requires_complete_calendar_and_matched_month():
    dates = pd.date_range("2024-01-01", "2024-02-29")
    daily = pd.Series(100., index=dates)
    months = pd.date_range("2024-01-31", periods=2, freq="ME")
    official = pd.Series([98., 105.], index=months)
    result = reconciliation(official, daily, months)
    assert result.publisher_minus_daily_mean.tolist() == [-2., 5.]
    for bad_official, bad_daily in [(official.iloc[:1], daily), (official, daily.iloc[:-1])]:
        with pytest.raises(ValueError, match="incomplete"):
            reconciliation(bad_official, bad_daily, months)


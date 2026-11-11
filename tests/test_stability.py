from src.stability import period_labels, rolling_starts
import pandas as pd
import numpy as np
import pytest


def test_period_partition_and_calendar_gap_guard():
    dates = pd.date_range("2000-10-31", periods=306, freq="ME")
    labels = period_labels(dates)
    assert np.bincount(labels).tolist() == [102, 102, 102]
    with pytest.raises(ValueError):
        period_labels(dates.delete(20))
    bad = dates.to_list()
    bad[20] = bad[19]
    with pytest.raises(ValueError):
        period_labels(pd.DatetimeIndex(bad))


def test_rolling_windows_include_final_without_duplicate_or_partial():
    starts = rolling_starts(306)
    assert starts[-1] == 186
    assert len(starts) == len(set(starts)) == 17
    assert all(s + 120 <= 306 for s in starts)
    assert rolling_starts(120) == [0]
    with pytest.raises(ValueError):
        rolling_starts(119)

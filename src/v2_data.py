"""Explicit vendor conventions and auditable calendar-month transformations."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import CONFIG, ROOT

CACHE = ROOT / "data/raw/v2/yahoo_daily.csv"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fetch() -> None:
    """Fetch once. Existing receipts are immutable; move cache to refresh explicitly."""
    import yfinance as yf
    receipt = CACHE.with_suffix(".json")
    if receipt.exists():
        read_market()
        return
    started = datetime.now(timezone.utc).isoformat()
    data = yf.download(list(CONFIG.tickers), start=CONFIG.start,
                       end=CONFIG.end_exclusive, auto_adjust=False,
                       back_adjust=False, repair=False, actions=True,
                       threads=False, progress=False, keepna=True)
    if data.empty or any(t not in data["Close"] or data["Close"][t].dropna().empty
                         for t in CONFIG.tickers):
        raise ValueError("Incomplete vendor download; no receipt written")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(CACHE)
    receipt.write_text(json.dumps({
        "provider": "Yahoo Finance via yfinance", "yfinance": yf.__version__,
        "retrieved_start_utc": started,
        "retrieved_end_utc": datetime.now(timezone.utc).isoformat(),
        "start": CONFIG.start, "end_exclusive": CONFIG.end_exclusive,
        "tickers": CONFIG.tickers, "auto_adjust": False, "back_adjust": False,
        "repair": False, "actions": True, "keepna": True,
        "sha256": sha256(CACHE),
        "vintage_warning": "Current vendor vintage, not the missing April 2026 download."
    }, indent=2), encoding="utf-8")

def read_market() -> pd.DataFrame:
    receipt = json.loads(CACHE.with_suffix(".json").read_text())
    if receipt["sha256"] != sha256(CACHE):
        raise ValueError("Market cache checksum mismatch")
    frame = pd.read_csv(CACHE, header=[0, 1], index_col=0, parse_dates=True)
    validate_dates(frame.index)
    return frame

def validate_dates(index: pd.DatetimeIndex) -> None:
    if not isinstance(index, pd.DatetimeIndex) or index.hasnans or index.has_duplicates:
        raise ValueError("Dates must be unique, nonmissing timestamps")
    if not index.is_monotonic_increasing:
        raise ValueError("Dates must be sorted")

def log_returns(prices: pd.Series) -> pd.Series:
    """No fill or bridging missing calendar months; invalid endpoints stay missing."""
    if np.isinf(prices.dropna()).any():
        raise ValueError("Infinite prices")
    return np.log(prices.where(prices > 0)).diff()

def monthly_prices(daily: pd.Series) -> pd.DataFrame:
    validate_dates(daily.index)
    valid = daily.dropna()
    if valid.empty:
        raise ValueError("Empty price series")
    price = valid.resample("ME").last()
    dates = pd.Series(valid.index, index=valid.index).resample("ME").last()
    return pd.DataFrame({"price": price, "source_date": dates,
                         "return": log_returns(price)})

def monthly_gpr(daily: pd.Series) -> pd.DataFrame:
    validate_dates(daily.index)
    if (daily.dropna() < 0).any() or np.isinf(daily.dropna()).any():
        raise ValueError("Invalid GPR values")
    result = daily.resample("ME").agg(["mean", "count"])
    result.columns = ["gpr", "days_observed"]
    result["days_expected"] = result.index.days_in_month
    result["complete"] = result.days_observed == result.days_expected
    return result

def read_gpr() -> pd.Series:
    gpr = pd.read_excel(ROOT / "data/raw/data_gpr_daily_recent.xls", engine="xlrd")
    return gpr.set_index("date")["GPRD"]

def build_panel(market: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    gpr = monthly_gpr(read_gpr())
    index = pd.date_range(CONFIG.start, CONFIG.complete_through, freq="ME")
    panel = pd.DataFrame(index=index)
    for name, field, ticker in [("xle", "Adj Close", "XLE"),
                                 ("xle_price", "Close", "XLE"),
                                 ("oil", "Close", "CL=F"),
                                 ("market", "Close", "^GSPC")]:
        monthly = monthly_prices(market[field][ticker])
        panel[name] = monthly["return"]
        panel[name + "_date"] = monthly["source_date"]
        if name == "oil":
            panel["oil_dollars"] = monthly.price.diff()
    panel["gpr100"] = gpr.gpr.where(gpr.complete) / 100
    panel["dgpr"] = log_returns(panel.gpr100)
    # Lag on the full calendar grid BEFORE any sample deletion.
    for column in ["gpr100", "dgpr", "xle", "oil", "market"]:
        for lag in (1, 2):
            panel[f"{column}_lag{lag}"] = panel[column].shift(lag)
    return panel, gpr

def common_date_returns(market: pd.DataFrame) -> pd.DataFrame:
    """Sensitivity: select last date per month with all three market quotes."""
    daily = pd.DataFrame({"xle": market["Adj Close"]["XLE"],
                          "oil": market["Close"]["CL=F"],
                          "market": market["Close"]["^GSPC"]}).dropna()
    prices = daily.resample("ME").last()
    return prices.apply(log_returns)

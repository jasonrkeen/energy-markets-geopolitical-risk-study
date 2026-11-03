"""Publisher archives and EIA Cushing spot price observations used by the revised study."""
from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen

import numpy as np
import pandas as pd

from src.config import CONFIG, ROOT
from src.v2_data import monthly_gpr, read_gpr, sha256, validate_dates

DIRECTORY = ROOT / "data/raw/spot_review"
ARCHIVE = ("https://raw.githubusercontent.com/iacoviel/iacoviel.github.io/"
           "259210729676a533a1256b512ab47c41f52fe2f0/gpr_archive_files/")
URLS = {"spot.xls": "https://www.eia.gov/dnav/pet/hist_xls/RWTCd.xls",
        "monthly.xls": ARCHIVE + "data_gpr_export_202604.xls",
        "daily.xls": ARCHIVE + "data_gpr_daily_recent_20260427.xls"}
SPOT_LABEL = "Cushing, OK WTI Spot Price FOB (Dollars per Barrel)"


def source_receipt(directory: Path) -> dict:
    receipt = json.loads((directory / "receipt.json").read_text())
    for name, url in URLS.items():
        item = receipt[name]
        if item["url"] != url or item["sha256"] != sha256(directory / name):
            raise ValueError(f"Official source URL or checksum mismatch for {name}")
    return receipt


def fetch_official() -> None:
    if DIRECTORY.exists():
        source_receipt(DIRECTORY)
        return
    DIRECTORY.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=DIRECTORY.parent) as temporary:
        stage = Path(temporary) / "official"
        stage.mkdir()
        receipt = {}
        for name, url in URLS.items():
            with urlopen(url, timeout=60) as response:
                (stage / name).write_bytes(response.read())
            receipt[name] = dict(url=url, sha256=sha256(stage / name),
                                 retrieved_utc=datetime.now(timezone.utc).isoformat())
        (stage / "receipt.json").write_text(json.dumps(receipt, indent=2))
        read_official(stage)
        stage.rename(DIRECTORY)


def read_official(directory: Path = DIRECTORY) -> tuple[pd.Series, pd.Series, dict]:
    receipt = source_receipt(directory)
    raw = pd.read_excel(directory / "spot.xls", sheet_name="Data 1", header=None)
    if tuple(raw.iloc[1, :2]) != ("Sourcekey", "RWTC") or tuple(raw.iloc[2, :2]) != ("Date", SPOT_LABEL):
        raise ValueError("Unexpected EIA daily series")
    spot = pd.Series(pd.to_numeric(raw.iloc[3:, 1]).to_numpy(),
                     index=pd.DatetimeIndex(raw.iloc[3:, 0]), name="spot_usd_per_barrel")
    validate_dates(spot.index)
    if np.isinf(spot.dropna()).any():
        raise ValueError("Infinite EIA spot quote")
    table = pd.read_excel(directory / "monthly.xls", usecols=["month", "GPR"])
    dates = pd.DatetimeIndex(table.month)
    validate_dates(dates)
    if not dates.is_month_start.all():
        raise ValueError("Expected publisher month-start labels")
    official = pd.Series(table.GPR.to_numpy(), index=dates + pd.offsets.MonthEnd(0), name="publisher_monthly")
    official = official.dropna()
    if not np.isfinite(official).all() or (official <= 0).any():
        raise ValueError("Invalid official GPR")
    archive = pd.read_excel(directory / "daily.xls", usecols=["date", "GPRD"]).set_index("date").GPRD
    retained = read_gpr()
    if not archive.index.equals(retained.index) or not np.array_equal(archive, retained, equal_nan=True):
        raise ValueError("Publisher archive differs from retained daily GPR values or dates")
    details = dict(downloads=receipt, matched_daily_rows=len(archive),
                   eia_last_available=str(spot.index.max().date()), monthly_last_available=str(official.index.max().date()))
    return spot.loc[:CONFIG.complete_through], official.loc[:CONFIG.complete_through], details


def reconciliation(official: pd.Series, daily: pd.Series, index: pd.DatetimeIndex) -> pd.DataFrame:
    means = monthly_gpr(daily)
    result = means.reindex(index).rename(columns={"gpr": "retained_daily_mean"})
    result["publisher_monthly"] = official.reindex(index)
    if result.isna().any().any() or not result.complete.all():
        raise ValueError("Unmatched or incomplete GPR comparison month")
    result["publisher_minus_daily_mean"] = result.publisher_monthly - result.retained_daily_mean
    return result

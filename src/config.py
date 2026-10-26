"""Fixed historical scope; no live 'today' defaults in model construction."""
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Config:
    start: str = "1998-01-01"
    end_exclusive: str = "2026-05-01"
    complete_through: str = "2026-03-31"
    comparison_start: str = "2000-10-31"
    replay_through: str = "2026-04-28"
    hac_lags: tuple[int, ...] = (3, 6, 12)
    max_endpoint_age_days: int = 4
    tickers: tuple[str, ...] = ("XLE", "CL=F", "^GSPC", "BP", "SHEL", "XOM", "CVX")

CONFIG = Config()

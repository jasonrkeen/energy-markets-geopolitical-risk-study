"""Preserve V1; replay all code cells with a dated vendor cache in isolation."""
import contextlib
import hashlib
import io
import json
import os
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import yfinance as yf

from src.config import CONFIG, ROOT
from src.v2_data import monthly_gpr, read_gpr, sha256

PRESERVED = ["notebooks/analysis.ipynb", "data/processed/xle_monthly.csv",
             "data/raw/data_gpr_daily_recent.xls", "outputs/charts/oil_betas.png",
             "outputs/charts/xle_vs_oil.png", "outputs/tables/xle_scenario_forecast.csv"]

def summary(result) -> dict:
    return {"n": int(result.nobs), "r_squared": float(result.rsquared),
            "coefficients": result.params.to_dict(), "pvalues": result.pvalues.to_dict()}

def verify_frozen_inputs(root: Path = ROOT) -> dict:
    """Compare to the original Git commit, not merely to the start of this run."""
    frozen = json.loads((root / "docs/v1/FROZEN_INPUTS.json").read_text())
    for name, expected in frozen["files"].items():
        data = (root / name).read_bytes()
        if expected["normalize_lf"]:
            data = data.replace(b"\r\n", b"\n")
        if hashlib.sha256(data).hexdigest() != expected["sha256"]:
            raise ValueError(f"Frozen V1 input differs from base commit: {name}")
    return frozen

def audit(market: pd.DataFrame, destination: Path) -> dict:
    frozen = verify_frozen_inputs()
    original_hashes = {p: sha256(ROOT / p) for p in PRESERVED}
    archived = pd.read_csv(ROOT / "data/processed/xle_monthly.csv", index_col=0, parse_dates=True)
    gpr = monthly_gpr(read_gpr())
    archived_panel = archived.join(gpr[["gpr"]], how="inner").dropna()
    exact = sm.OLS(archived_panel["return"], sm.add_constant(archived_panel[["gpr"]])).fit()
    ret_error = float((np.log(archived.price).diff() - archived["return"]).abs().max())
    notebook = json.loads((ROOT / "notebooks/analysis.ipynb").read_text(encoding="utf-8"))
    sandbox = destination / "replay"
    for subdir in ["notebooks", "data/raw", "data/processed", "outputs/charts", "outputs/tables"]:
        (sandbox / subdir).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "data/raw/data_gpr_daily_recent.xls", sandbox / "data/raw/data_gpr_daily_recent.xls")
    cutoff = market.loc[:CONFIG.replay_through]
    original_download = yf.download
    def cached_download(tickers, **kwargs):
        symbols = [tickers] if isinstance(tickers, str) else tickers
        selected = cutoff.loc[:, cutoff.columns.get_level_values(1).isin(symbols)].copy()
        if kwargs.get("auto_adjust", True):
            for ticker in symbols:
                factor = selected[("Adj Close", ticker)] / selected[("Close", ticker)]
                for field in ["Open", "High", "Low", "Close"]:
                    selected[(field, ticker)] *= factor
            selected = selected.drop(columns="Adj Close", level=0)
        selected = selected.dropna(how="all")
        return selected.swaplevel(axis=1).sort_index(axis=1) if kwargs.get("group_by") == "ticker" else selected
    namespace = {"__name__": "__main__"}
    stdout = io.StringIO()
    cwd = Path.cwd()
    completed = []
    try:
        yf.download = cached_download
        os.chdir(sandbox / "notebooks")
        with contextlib.redirect_stdout(stdout):
            for i, cell in enumerate(notebook["cells"]):
                if cell["cell_type"] == "code":
                    exec(compile("".join(cell["source"]), f"v1_cell_{i}", "exec"), namespace)
                    completed.append(i)
                    plt.close("all")
    finally:
        os.chdir(cwd)
        yf.download = original_download
    (destination / "v1_replay_stdout.txt").write_text(stdout.getvalue(), encoding="utf-8")
    result = namespace["scenario_model"]
    original_scenarios = pd.read_csv(ROOT / "outputs/tables/xle_scenario_forecast.csv")
    reproduced_scenarios = namespace["scenario_output"]
    delta = reproduced_scenarios.select_dtypes("number") - original_scenarios.select_dtypes("number")
    delta.insert(0, "Scenario", original_scenarios.Scenario)
    delta.to_csv(destination / "v1_scenario_replay_deltas.csv", index=False)
    replay_monthly = namespace["monthly"]
    comparison = pd.DataFrame({"archived_return": archived["return"], "replay_return": replay_monthly["return"]})
    comparison["difference"] = comparison.replay_return - comparison.archived_return
    comparison.to_csv(destination / "v1_xle_return_deltas.csv")
    if any(sha256(ROOT / p) != h for p, h in original_hashes.items()):
        raise RuntimeError("V1 artifact changed during replay; output publication aborted")
    evidence = {
        "status": "PARTIAL_REPRODUCTION_CURRENT_VENDOR_VINTAGE",
        "frozen_base_commit": frozen["base_commit"],
        "matches_frozen_base": True,
        "original_hashes": original_hashes,
        "preserved_unchanged": all(sha256(ROOT / p) == h for p, h in original_hashes.items()),
        "cell_count": len(notebook["cells"]), "executed_cells": completed,
        "replay_method": "Original cell code via exec, cached yf.download substituted; tail expressions not rendered; plots regenerated in isolated sandbox. auto_adjust=True inferred for unspecified calls, not verified historically.",
        "original_execution_date_from_saved_output": "2026-04-28",
        "replay_market_through": CONFIG.replay_through,
        "archived_gpr_through": str(read_gpr().index.max().date()),
        "archived_xle_log_return_max_abs_error": ret_error,
        "archived_xle_gpr_model": summary(exact),
        "replayed_final_model": summary(result),
        "replay_sample_start": str(namespace["X"].index.min().date()),
        "replay_sample_end": str(namespace["X"].index.max().date()),
        "max_xle_return_replay_abs_difference": float(comparison.difference.abs().max()),
        "max_scenario_replay_difference_percentage_points": float(delta["Forecast XLE Return (%)"].abs().max()),
        "unresolved": ["Original daily Yahoo downloads and environment were not retained.",
                       "Current-vintage replay cannot establish byte-identical historical provenance.",
                       "GPR workbook retrieval date and historical source hash are unknown."]
    }
    (destination / "v1_audit.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    return evidence

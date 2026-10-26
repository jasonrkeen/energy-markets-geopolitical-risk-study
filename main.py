"""Run `python main.py --fetch` once, then `python main.py` for offline reproduction."""
import argparse
import importlib.metadata
import json
import platform
from dataclasses import asdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import CONFIG, ROOT
from src.v1_audit import audit
from src.v2_data import CACHE, build_panel, common_date_returns, content_hash, fetch, read_market, sha256
from src.v2_models import estimate, fit, scenario_log_prediction
from src.run_artifacts import staged_output

def run_pipeline(out: Path) -> dict:
    market = read_market()
    out.mkdir(parents=True, exist_ok=True)
    evidence = audit(market, out)
    panel, gpr = build_panel(market)
    coefficients, joint, ledger = estimate(panel)
    panel.to_csv(out / "monthly_panel.csv")
    gpr.to_csv(out / "gpr_coverage.csv")
    ledger.to_csv(out / "sample_ledger.csv")
    coefficients.to_csv(out / "coefficients.csv", index=False)
    joint.to_csv(out / "joint_gpr_tests.csv", index=False)
    daily_oil = market["Close"]["CL=F"]
    daily_oil.loc[daily_oil <= 0].to_csv(out / "nonpositive_daily_oil.csv")
    main_rows = coefficients.query("model == 'xle_full' and covariance == 'HAC6'")
    common = panel.loc[ledger.included_common]
    result = fit(common, "xle", ["gpr100", "oil", "market"])
    from statsmodels.stats.diagnostic import acorr_ljungbox, het_breuschpagan
    from statsmodels.stats.stattools import durbin_watson
    diagnostics = {"durbin_watson": float(durbin_watson(result.resid)),
        "ljung_box_residuals_lag12_p": float(acorr_ljungbox(result.resid, lags=[12], return_df=True).lb_pvalue.iloc[0]),
        "breusch_pagan_lm_p": float(het_breuschpagan(result.resid, result.model.exog)[1]),
        "interpretation": "Descriptive specification diagnostics; no causal validation or model selection by p-value."}
    (out / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2))
    influence = result.get_influence()
    pd.DataFrame({"cooks_distance": influence.cooks_distance[0],
                  "leverage": influence.hat_matrix_diag}, index=common.index).to_csv(out / "influence.csv")
    endpoints = pd.DataFrame(index=panel.index)
    for name in ["xle", "xle_price", "oil", "market"]:
        endpoints[name + "_calendar_days_before_month_end"] = (panel.index.to_series() - panel[name + "_date"]).dt.days
    endpoints["oil_equity_source_dates_match"] = panel.oil_date == panel.xle_date
    endpoints.to_csv(out / "endpoint_audit.csv")
    # Full eligible baseline separately documents sample cost of shared lag comparisons.
    full = fit(panel, "xle", ["gpr100", "oil", "market"])
    from src.v1_audit import summary
    aligned = common_date_returns(market).join(panel[["gpr100"]]).reindex(common.index)
    aligned_result = fit(aligned, "xle", ["gpr100", "oil", "market"])
    alignment_summary = summary(aligned_result)
    alignment_summary["covariance"] = "HAC6"
    alignment_summary["definition"] = "Last date in each month with all three market quotes; GPR still full calendar-month mean. Same 306 months."
    (out / "common_date_sensitivity.json").write_text(json.dumps(alignment_summary, indent=2))
    (out / "baseline_full_sample.json").write_text(json.dumps(summary(full), indent=2))
    scenarios = []
    for label, oil, equity in [("Bear", -.10, -.05), ("Base", 0, .01), ("Bull", .08, .04),
                                ("Oil shock", .15, -.02), ("Market selloff", -.05, -.10)]:
        risk = float(common.gpr100.median())
        x = np.array([1, risk, np.log1p(oil), np.log1p(equity)])
        pred = result.get_prediction(x).summary_frame(alpha=.05).iloc[0]
        scenarios.append(dict(scenario=label, gpr100=risk, oil_simple=oil, market_simple=equity,
            fitted_log_return=float(pred["mean"]),
            simple_equivalent_return=scenario_log_prediction(result.params, risk, oil, equity),
            simple_equivalent_mean_log_ci_low=np.expm1(pred.mean_ci_lower),
            simple_equivalent_mean_log_ci_high=np.expm1(pred.mean_ci_upper)))
    pd.DataFrame(scenarios).to_csv(out / "conditional_scenarios.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    subset = main_rows.loc[main_rows.term != "const"].set_index("term")
    ax.errorbar(subset.coefficient, range(len(subset)),
                xerr=[subset.coefficient-subset.ci_low, subset.ci_high-subset.coefficient], fmt="o", capsize=4)
    ax.set_yticks(range(len(subset)), ["GPR (100 index points)", "Oil proxy (log change)", "S&P 500 (log return)"])
    ax.axvline(0, color="grey", linewidth=1)
    ax.set_xlabel("Coefficient and 95% HAC(6) confidence interval")
    ax.set_title(f"XLE conditional associations | n={int(result.nobs)} | through March 2026")
    fig.tight_layout()
    fig.savefig(out / "xle_coefficients.png", dpi=160)
    plt.close(fig)
    versions = {x: importlib.metadata.version(x) for x in
                ["pandas", "numpy", "scipy", "statsmodels", "matplotlib", "yfinance", "xlrd"]}
    receipt = json.loads(CACHE.with_suffix(".json").read_text())
    manifest = {"config": asdict(CONFIG), "packages": versions, "market_receipt": receipt,
                "python_version": platform.python_version(), "platform": platform.platform(),
                "gpr_sha256": sha256(ROOT / "data/raw/data_gpr_daily_recent.xls"),
                "gpr_vintage": "Retained V1 workbook through 2026-04-27; retrieval date unknown",
                "results_status": "Exploratory, current market vintage plus retained GPR vintage",
                "complete_month_cutoff": CONFIG.complete_through,
                "common_sample_n": int(result.nobs), "common_sample_start": str(common.index.min().date()),
                "common_sample_end": str(common.index.max().date()),
                "v1_preserved": evidence["preserved_unchanged"]}
    manifest["artifact_hash_scheme"] = "SHA256; CRLF normalized to LF in text artifacts; binary files unchanged. Input cache SHA256 remains exact bytes."
    manifest["source_code_hashes"] = {str(p.relative_to(ROOT)).replace("\\", "/"): content_hash(p)
        for p in [ROOT / "main.py", ROOT / "requirements-lock.txt", ROOT / "docs/v1/FROZEN_INPUTS.json", *sorted((ROOT / "src").glob("*.py"))]}
    manifest["artifact_hashes"] = {p.name: content_hash(p) for p in sorted(out.iterdir()) if p.is_file() and p.name != "manifest.json"}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"v1": evidence["replayed_final_model"], "v2": summary(result),
            "common_sample_start": manifest["common_sample_start"]}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Fetch only if no cache receipt exists")
    parser.add_argument("--verify-repeat", action="store_true", help="Actually run twice and compare all CSVs")
    args = parser.parse_args()
    if args.fetch:
        fetch()
    destination = ROOT / "outputs/v2"
    with staged_output(destination) as stage:
        result = run_pipeline(stage)
        if args.verify_repeat:
            from tempfile import TemporaryDirectory
            with TemporaryDirectory() as directory:
                repeat = Path(directory)
                run_pipeline(repeat)
                before = {p.name: content_hash(p) for p in stage.glob("*.csv")}
                after = {p.name: content_hash(p) for p in repeat.glob("*.csv")}
                if not before or before != after:
                    raise ValueError("Repeated CSV outputs differ")
                receipt = {"offline_numeric_csvs_identical": True, "csv_count": len(before),
                           "hash_scheme": "SHA256 after CRLF-to-LF normalization", "sha256": before}
                (stage / "reproducibility_check.json").write_text(json.dumps(receipt, indent=2))
                manifest = json.loads((stage / "manifest.json").read_text())
                manifest["artifact_hashes"]["reproducibility_check.json"] = content_hash(stage / "reproducibility_check.json")
                (stage / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps({**result, "output": str(destination)}, indent=2))

if __name__ == "__main__":
    main()

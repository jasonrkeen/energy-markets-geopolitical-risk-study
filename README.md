# Energy markets and geopolitical risk

**Release candidate, November 11, 2026.** [Current report and stability review](docs/RELEASE_CANDIDATE.md) | [Clean-environment validation](docs/CLEAN_VALIDATION.json). [Final red-team review](docs/FINAL_RED_TEAM.md) recommends merge within the retrospective scope; PR #1 remains draft for the owner's decision. Oil exposure is positive across the reported checks; full-model instability and residual dependence remain.

XLE had an estimated Cushing WTI spot-price exposure of **0.322** over 306 completed months from October 2000 through March 2026. A 1% higher monthly spot-price change was associated with approximately 0.32% higher XLE return, conditional on S&P 500 return and publisher monthly GPR. The 95% HAC interval was 0.235 to 0.408. The matched CL=F sensitivity gave 0.321. The GPR coefficient had p=0.089. These are retrospective associations.

[Current findings, source reconciliation and methodological limits](docs/SPOT_GPR_RECONCILIATION.md) · [Source manifest](outputs/v2/manifest.json) · [Matched results](outputs/v2/matched_proxy_comparisons.csv)

![Conditional estimates](outputs/v2/xle_coefficients.png)

## Reproduce

Use Python 3.14 in a virtual environment at the repository root.

```sh
python -m pip install -r requirements-lock.txt
python main.py --fetch --verify-repeat
python -m pytest -q
```

The initial fetch caches the daily Yahoo market fields, EIA RWTC workbook and archived publisher GPR workbooks. Use `python main.py --verify-repeat` for offline runs with those caches. The EIA and Yahoo histories can revise. See the current report for acquisition details and original-vintage limits.

## Historical material

The original notebook is preserved and replayed in isolation. The October draft used CL=F and a daily-average GPR index as its primary inputs. Its review records are retained for comparison. [V1 README](docs/v1/README.md) · [October methodology](docs/METHODOLOGY_V2.md) · [October review](docs/PR1_REVIEW.md)

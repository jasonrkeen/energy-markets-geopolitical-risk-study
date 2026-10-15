> This file mirrors `.github/copilot-instructions.md` and `CLAUDE.md`; keep all three in sync when any changes.

# AGENTS.md — energy-markets-geopolitical-risk-study

## Purpose
Empirical analysis of geopolitical risk and energy equity returns using Python

## Tech stack
- Python; dependencies in `requirements.txt`
- Key libraries: `pandas`, `numpy`, `matplotlib`, `statsmodels`, `yfinance`, `jupyter`, `openpyxl`

## Folder structure
- `data/` (2 files)
- `notebooks/` (1 files)
- `outputs/` (3 files)
- `src/` (3 files)
- `README.md`
- `requirements.txt`

## Setup, run, test
- `pip install -r requirements.txt`
- No automated tests exist yet; if adding them, use pytest under `tests/`.

## Conventions observed
- Public data sources referenced: yfinance.
- Write paths relative to the repo root (no absolute local paths).

## Output artifacts
- Generated outputs go to: `outputs/charts/`, `outputs/tables/`

## Guardrails
- Never commit secrets, API keys, tokens, or `.env` files.
- Do not commit large raw datasets or binaries; keep data fetched or documented with its source.
- Keep analysis source-backed: cite data sources and assumptions; label scenario/forecast outputs as model estimates, not facts.
- Preserve reproducibility: no unseeded randomness, no hidden manual steps.

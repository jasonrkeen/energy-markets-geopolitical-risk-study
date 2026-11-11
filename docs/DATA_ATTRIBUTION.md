# Third-party data attribution

## Geopolitical Risk index (CC BY 4.0)

Creators: Dario Caldara and Matteo Iacoviello.

Cite: Caldara, Dario and Matteo Iacoviello (2022), "Measuring Geopolitical Risk," American Economic Review, 112(4), 1194-1225.

Source and license notice: https://www.matteoiacoviello.com/gpr.htm
License: Creative Commons Attribution 4.0 International, https://creativecommons.org/licenses/by/4.0/

Publisher archive root used: https://raw.githubusercontent.com/iacoviel/iacoviel.github.io/259210729676a533a1256b512ab47c41f52fe2f0/gpr_archive_files/

- `data_gpr_export_202604.xls`, locally named `monthly.xls`, downloaded November 3, 2026 UTC (November 2 Chicago). SHA-256: da487ad52540e133a1d316875c9ae6657ddd6efd7c06dd4b8332718fbad59f0a.
- `data_gpr_daily_recent_20260427.xls`, locally named `daily.xls`, downloaded November 3, 2026 UTC (November 2 Chicago). SHA-256: 72213d279a3488dfa9e4bbf70c559b118716fcf24553091dd01d4b60b0c532e1.

These two workbooks are unchanged from the downloaded bytes; only local filenames and packaging differ. The previously retained `data/raw/data_gpr_daily_recent.xls` has an unknown acquisition date and different bytes; its GPRD values and dates match the publisher daily archive. That comparison does not authenticate its original acquisition.

Study transformations: calendar-month mapping, sample cutoff, scaling GPR by 100, log differences and lags, and arithmetic daily means for a separate sensitivity. Derived GPR tables are marked as study transformations and are not publisher revisions. Credit the creators, cite the license and indicate further changes when reusing them. No author endorsement is implied. This license attribution does not cover market data from other providers.

## Other source acknowledgments

Cushing WTI observations were obtained through the U.S. Energy Information Administration, RWTC daily workbook, acquired November 2, 2026 Chicago. EIA's spot-price publications identify Refinitiv/LSEG as a source; downstream redistribution clearance remains unresolved for the cached workbook, which is not included.

Market data were obtained from Yahoo Finance through yfinance on October 26, 2026 UTC. The daily cache is not included. Yahoo/third-party rights are not conveyed by this repository's MIT software license. See DATA_REDISTRIBUTION.md for exclusions, legacy exposure and reproduction limits.

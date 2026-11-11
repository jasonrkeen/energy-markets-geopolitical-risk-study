# Cached-data redistribution review

Reviewed November 11, 2026 for the v2.0.0 release assets. This is a source-based permissions assessment, not a determination of every applicable contractual, database or copyright right. The release tag and scientific findings are unchanged; the attached bundle is distribution revision 2.

| Material | Public-bundle decision | Basis and remaining boundary |
|---|---|---|
| Publisher monthly and daily GPR archive workbooks | Include exact cached bytes with CC BY 4.0 attribution | The publisher's page explicitly licenses all its material for redistribution and links the older-vintage archive. Applying that notice to the linked publisher archive is the basis for inclusion. |
| Retained V1 GPR workbook | Include with attribution and provenance caveat | All 15,092 dates and GPRD readings match the publisher archive, but file bytes differ and the original acquisition receipt is absent. Do not represent it as a byte-authenticated publisher download. |
| Yahoo daily market cache | Exclude | Yahoo's Finance help page says: "You must not redistribute information displayed on or provided by Yahoo Finance." No redistribution agreement was found. |
| EIA RWTC spot workbook | Withhold pending series-specific clarification | EIA permits reuse of its own content but excludes protected third-party resources. Its daily-price page identifies Refinitiv wholesale spot data republished with permission. This does not prove that all RWTC history is restricted, but it prevents treating this workbook as unambiguously public-domain EIA-authored data. |
| Full Yahoo-derived price/return histories and mixed monthly panel | Exclude from revised ZIP pending permission | Changing frequency or taking log returns is not, by itself, evidence of redistribution permission. The original XLE CSV, replay return history and mixed panel reproduce extensive observations. |
| Research coefficients, tests, diagnostics, scenario summaries and narrative | Retain as research outputs | These summarize the study rather than supply a replacement market-data feed. This is an operational distinction, not a blanket legal clearance for every possible derived-data use. Seek advice or provider permission for commercial redistribution. |
| Repository software | Retain existing MIT license | The repository's software license does not relicense third-party datasets. |

## Primary sources checked

- [GPR publisher](https://www.matteoiacoviello.com/gpr.htm): explicit open-access redistribution statement, author attribution request, archive links and suggested citation/download date.
- [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): permits sharing and adaptation, including commercial use, subject to attribution, license reference and indication of changes. It does not imply endorsement or grant rights the licensor does not hold.
- [Yahoo Finance data providers](https://help.yahoo.com/kb/SLN2310.html): the prohibition quoted above was retrieved directly with HTTP 200. Browser-reader attempts returned 429; the recorded source receipt corresponds to the successful direct fetch.
- [Yahoo terms](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html) and [yfinance documentation](https://ranaroussi.github.io/yfinance/): access through an open-source library does not supply redistribution rights to the downloaded data. The library describes personal-use limits and directs users to Yahoo's terms.
- [EIA copyright and reuse](https://www.eia.gov/about/copyrights_reuse.php) and [EIA daily prices](https://www.eia.gov/TodayinEnergy/prices.php): general reuse permission has a protected-material exception; the price page identifies third-party suppliers. No explicit downstream redistribution grant for the cached RWTC workbook was established.

The sources were checked at the review date; this does not establish their exact wording when the data were acquired. Local HTML evidence is retained privately. URLs, retrieval times and SHA-256 hashes are in REDISTRIBUTION_SOURCE_RECEIPTS.json.

## Revision 2 asset contents and reproducibility

Added the publisher April 2026 monthly workbook and April 27 daily workbook unchanged, under `data/redistributable/gpr/`, with their original receipt entries and attribution. This separate directory intentionally avoids creating a partial `data/raw/spot_review/` cache: the existing pipeline requires that cache to contain all three official-source files.

The revised public ZIP omits the original XLE price CSV, mixed monthly panel, full replay-return comparison, nonpositive oil observation file, saved notebook outputs, historical raw-data plot and date-level influence values. Code, hashes, licensed GPR observations and aggregate research evidence remain. The manifest lists every omitted path and why. The original full-input archive remains local and unchanged.

This is now a partial reproduction kit, not a self-contained offline executable archive. Running `main.py`, all preservation tests, or the frozen PDF builder additionally requires the omitted V1 evidence and authorized market/spot inputs matching the documented hashes. A provider re-download is not guaranteed to recover those bytes. Obtain lawful inputs or permission before completing the archive; do not bypass the frozen-input checks. GPR snapshots alone cannot reproduce the market models.

## Unresolved public exposure and next steps

The existing Git history, v2.0.0 tag and GitHub-generated source archives still contain previously committed price/return observations and notebook outputs. Replacing a release ZIP does not remove these. No history was rewritten and no frozen original was deleted. Therefore this review does **not** certify the entire public repository as redistribution-cleared. A separate remediation decision is needed: obtain permission or preserve the evidence privately and prepare a cleaned public history/new repository. GitHub source-archive links are not substitutes for the curated revision 2 ZIP.

Request series-specific downstream rights from EIA/Refinitiv for RWTC, and a redistribution license or alternative licensed source for Yahoo-derived data. No outreach was sent. If new permissions are obtained, retain them with the provenance records before expanding public assets. Distribution revision 2 keeps the original v2.0.0 tag fixed and provides new asset hashes; scientific estimates remain unchanged.

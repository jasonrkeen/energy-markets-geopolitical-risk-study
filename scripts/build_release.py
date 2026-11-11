"""Build the two-page executive brief from generated CSVs and a validation receipt.

Run after main.py --verify-repeat and the clean-environment check.
Optional publishing dependency: reportlab==4.4.9.
"""
import csv
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from release_inputs import validate_release_inputs
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/release-candidate'


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader((ROOT/'outputs/v2/stability_estimates.csv').open()))
    oil = {r['model']: r for r in rows if r['term'] == 'oil'}
    checks = validate_release_inputs(ROOT)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Deck', fontSize=12, leading=17, textColor=colors.HexColor('#42576b'), spaceAfter=14))
    styles['Title'].textColor = colors.HexColor('#102f48')
    styles['Title'].fontSize = 24
    styles['Title'].leading = 29
    styles['BodyText'].fontSize = 10
    styles['BodyText'].leading = 14
    styles['BodyText'].spaceAfter = 9
    styles['Heading2'].textColor = colors.HexColor('#102f48')
    story = []
    def para(text: str, style: str = 'BodyText') -> None:
        story.append(Paragraph(text, styles[style]))
    para('XLE and oil-price exposure', 'Title')
    para('Release candidate | Jason Keen | November 11, 2026<br/>Historical study: October 2000-March 2026', 'Deck')
    para('A positive historical association, with limits to stability', 'Heading2')
    para('Across 306 months, a 1% higher Cushing WTI spot-price change was associated with approximately 0.32% higher XLE return, conditional on the S&amp;P 500 price return and monthly geopolitical risk. The oil coefficient is 0.322, with a 95% HAC interval of 0.235-0.408. This is an estimated historical association.')
    para('The matched CL=F sensitivity gives 0.321. The primary model explains about 59% of in-sample return variation. Neither statistic establishes predictive performance or a causal transmission mechanism.')
    para('Stability review', 'Heading2')
    table=[['Specification / period','Months','Oil exposure','95% interval']]
    labels=[('baseline','Full sample'),('period_1','Oct 2000-Mar 2009'),('period_2','Apr 2009-Sep 2017'),('period_3','Oct 2017-Mar 2026'),('exclude_covid','Exclude Mar-Jun 2020'),('lagged_xle','Add lagged XLE return')]
    for key,label in labels:
        r=oil[key];table.append([label,r['n'],f"{float(r['beta']):.3f}",f"{float(r['ci_low']):.3f} to {float(r['ci_high']):.3f}"])
    t=Table(table,colWidths=[210,48,80,130], repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#102f48')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#edf3f7'),colors.white])]))
    story += [t,Spacer(1,12)]
    para('The oil-slope equality test does not detect differences across the three periods (adjusted p=0.976). However, the joint test of all model coefficients changing gives adjusted p=0.048. Rolling ten-year oil estimates range from 0.213 to 0.348. Non-rejection for oil alone does not establish constant exposure.')
    story.append(PageBreak())
    para('What this release supports', 'Title')
    para('Evidence, validation and remaining boundaries', 'Deck')
    para('Geopolitical risk remains inconclusive', 'Heading2')
    para('The primary GPR coefficient has p=0.089 and an interval spanning zero. The market-controlled GPR-oil test has p=0.787. None of the eleven joint GPR tests passes the 5% threshold after Holm correction (smallest adjusted p=0.570). These results do not demonstrate absence of an effect or mediation through oil.')
    para('Residual dependence remains', 'Heading2')
    para('The baseline residual diagnostic gives p=0.015. Adding one lagged XLE return raises oil exposure to 0.352 but leaves residual dependence (approximate diagnostic p=0.025). Robust standard errors do not repair omitted dynamics, unstable parameters or causal identification.')
    para('Sources and calendar alignment', 'Heading2')
    para('EIA Cushing WTI spot is primary; CL=F is a stitched futures-price sensitivity. Publisher monthly GPR is primary; the retained daily average is a sensitivity. All 306 months have complete source inputs. Eighteen month-end observations use different oil and equity dates; the common-date estimate is 0.323. Quote-date auditing does not establish synchronized intraday pricing or an independently verified holiday calendar.')
    para('Validation completed', 'Heading2')
    para(f'A new isolated Python 3.14.4 environment installed the pinned analysis dependencies. A separate source copy passed {checks["tests_passed"]} tests and two cached-input pipeline runs; all 17 numerical CSVs matched the development run after documented line-ending normalization. Original V1 files remain preserved. This is same-machine clean-environment validation; the historical market download vintage remains unavailable.')
    para('Release decision and next steps', 'Heading2')
    para('Suitable for review as an exploratory historical exposure study. Keep PR #1 in draft pending reviewer acceptance. Forecasting requires a frozen protocol and genuinely untouched future observations. Causal claims require a defensible identification design. Archive exact source bytes subject to source terms; refreshed live downloads can revise history.')
    para('Sources and full evidence', 'Heading2')
    para('<link href="https://www.eia.gov/dnav/pet/hist/RWTCD.htm" color="#195b88">EIA Cushing WTI daily prices</link> | <link href="https://www.matteoiacoviello.com/gpr.htm" color="#195b88">Caldara-Iacoviello GPR</link> | <link href="https://github.com/jasonrkeen/energy-markets-geopolitical-risk-study/pull/1" color="#195b88">Draft PR and technical report</link><br/>Exact vintages, checksums, all sensitivity results and limitations are included in the reproduction bundle and RELEASE_CANDIDATE.md.')
    def footer(canvas, doc):
        canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#42576b'))
        canvas.drawString(42,25,'ENERGY MARKETS | Exploratory research | Release candidate')
        canvas.drawRightString(570,25,str(doc.page))
    SimpleDocTemplate(str(OUT/'executive-brief.pdf'),pagesize=(612,792),rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=40,title='XLE oil exposure - release candidate',author='Jason Keen').build(story,onFirstPage=footer,onLaterPages=footer)

if __name__ == '__main__':
    main()

# Energy Markets & Geopolitical Risk

## Overview

This project investigates whether **geopolitical risk impacts energy equity returns**, using:

- **XLE (Energy Select Sector SPDR Fund)** for sector-level analysis  
- **BP, Shell, Exxon Mobil, Chevron** for firm-level analysis  

The central question:

> Do energy stocks respond directly to geopolitical risk, or indirectly through oil prices?

---

## 🧠 Key Finding

> **Geopolitical risk does not directly drive energy equity returns.  
Instead, its impact is transmitted through oil prices.**

Geopolitical Risk → Oil Prices → Energy Equities

---

## 💡 Why This Matters

Energy markets are widely assumed to react directly to geopolitical events.  
This analysis shows instead:

- Markets do **not price geopolitical risk directly**  
- Geopolitical shocks are **absorbed by oil markets first**  
- Energy equities respond to **commodity price movements**

---

## 📚 Data Sources

- XLE & equities: yfinance  
- WTI crude oil futures  
- S&P 500 index  
- Geopolitical Risk Index (GPR) — Caldara & Iacoviello  
- U.S. Energy Information Administration (EIA)  
- International Energy Agency (IEA)  
- OPEC Monthly Oil Market Report  

---

## 🌍 Geopolitical Risk Measure (GPR)

The project uses the **Geopolitical Risk (GPR) Index**, a widely cited macroeconomic indicator.

### Methodology

- Built from text analysis of major global newspapers (FT, NYT, WSJ)  
- Measures frequency of articles related to:
  - wars  
  - terrorism  
  - geopolitical tensions  

Defined as:

> Share of news coverage focused on geopolitical risk

---

### Interpretation

- Captures both threats and realized events  
- Normalized so mean = 100  

---

### Source

Caldara, D., & Iacoviello  
https://www.matteoiacoviello.com/gpr.htm  

---

## ⚙️ Methodology

- Daily → monthly aggregation  
- Log returns computed  
- Regression models include oil and market controls  

```python
X = sm.add_constant(df[["gpr", "wti_return", "sp500_return"]])
y = df["return"]
model = sm.OLS(y, X).fit()
```

---

## 📈 Results

### Sector-Level (XLE)

- Oil returns → highly significant  
- S&P 500 → highly significant  
- GPR → not significant  

R² ≈ 0.57

---

### Firm-Level Analysis

| Company | Oil Sensitivity |
|--------|----------------|
| BP | ~0.35 |
| Shell | ~0.31 |
| Chevron | ~0.30 |
| Exxon | ~0.28 |

No firm shows significant sensitivity to geopolitical risk.

---

## 📊 Supporting Evidence

### Correlation

- XLE vs WTI: ~0.62  
- XLE vs GPR: ~0.00  

---

### Event Study

- Normal periods: ~0.0067  
- High GPR periods: ~0.0062  

No meaningful difference observed.

---

## 🔮 Scenario Forecasting

| Scenario | WTI (%) | S&P 500 (%) | XLE Forecast (%) |
|--------|--------|------------|----------------|
| Bear Case | -10 | -5 | -6.8 |
| Base Case | 0 | 1 | 0.8 |
| Bull Case | 8 | 4 | 5.7 |
| Oil Shock | 15 | -2 | 3.8 |
| Market Selloff | -5 | -10 | -8.8 |

Key insight:

> Oil shocks can offset broader market declines in energy equities.

---

## 📰 Real-World Validation

Recent geopolitical tensions involving Iran caused:

- Significant oil supply disruptions  
- Sharp increases in oil prices  
- Higher profits for energy firms such as BP  

This supports the model’s core mechanism:

> Geopolitical events impact energy equities indirectly through oil prices.

Source:  
https://www.msn.com/en-us/news/politics/bp-doubles-its-profits-as-iran-war-elevates-oil-prices/ar-AA21WtaC

---

## 🛢️ Energy Market Fundamentals (EIA & IEA)

Insights from EIA and IEA show:

- Short-term supply disruptions cause price spikes  
- Global demand growth is slowing  
- Inventories are expected to increase over time  

Interpretation:

> Oil prices are driven by supply-demand dynamics, acting as the transmission channel between geopolitical events and equity markets.

Sources:  
https://www.eia.gov/outlooks/steo/report/global_oil.php  
https://www.iea.org/reports/oil-market-report-april-2026  

---

## 🛢️ Oil Market Structure (OPEC Perspective)

OPEC analysis adds a supply-side perspective:

- Global demand expected to grow ~1.3–1.4 mb/d  
- Non-OPEC supply expanding  
- OPEC+ actively managing production  
- Geopolitical disruptions causing supply shocks  

Interpretation:

> Geopolitics affects energy markets through supply disruptions that drive oil prices.

Source:  
https://www.opec.org/assets/assetdb/momr-march-2026.pdf  

---

## 🎯 Final Takeaway

Across all analyses:

- Geopolitical risk is not a direct driver  
- Oil prices are the primary transmission channel  
- Market conditions remain the dominant factor  

---

## 🧠 Economic Insight

Markets are forward-looking and efficient.

By the time geopolitical risk rises:
- Oil prices have already adjusted  
- Expectations are already priced into equities  

---

## 🛠️ Tech Stack

- Python  
- pandas / numpy  
- statsmodels  
- matplotlib  
- yfinance  

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
```

Open:

notebooks/analysis.ipynb

---

## 👤 Author

Jason Keen

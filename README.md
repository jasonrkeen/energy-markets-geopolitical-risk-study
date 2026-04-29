# 📊 Energy Markets & Geopolitical Risk Analysis

Empirical analysis of how geopolitical risk impacts energy equities (XLE) using Python and econometric modeling.

---

## 🔑 Key Insight

> Geopolitical risk does not directly drive energy stock returns — its impact is transmitted through oil prices.

---

## 📈 XLE vs Oil Returns

![XLE vs Oil](outputs/charts/xle_vs_oil.png)

> Strong positive relationship between oil prices and energy equity returns (corr ≈ 0.62)

---

## 📊 Key Results

- Model explanatory power: **R² ≈ 0.57**
- Oil sensitivity: **β ≈ 0.32**
- Market exposure: **β ≈ 0.75**
- Correlation:
  - XLE vs GPR: ~0.00
  - XLE vs Oil: ~0.62

### 💡 Interpretation
Markets do not price geopolitical risk directly—they price its economic consequences through oil.

---

## 🛢️ Oil Sensitivity by Company

![Oil Betas](outputs/charts/oil_betas.png)

| Company | Oil Sensitivity |
|--------|----------------|
| BP | ~0.35 |
| Shell | ~0.31 |
| Chevron | ~0.30 |
| Exxon | ~0.28 |

---

## 🔮 Scenario Forecasting (XLE)

| Scenario | Oil Return | S&P 500 | Forecast XLE |
|--------|-----------|--------|-------------|
| Bear Case | -10% | -5% | **-6.8%** |
| Base Case | 0% | +1% | **+0.8%** |
| Bull Case | +8% | +4% | **+5.7%** |
| Oil Shock | +15% | -2% | **+3.8%** |
| Market Selloff | -5% | -10% | **-8.8%** |

> Oil shocks can offset weak equity markets, highlighting the sector’s unique exposure to commodity dynamics.

---

## 🌍 Geopolitical Risk (GPR)

The Geopolitical Risk Index (Caldara & Iacoviello) measures the share of global news coverage related to geopolitical tensions such as wars and terrorism.

- Baseline level ≈ 100  
- Crisis periods can exceed 150–300  

Despite these spikes, GPR is not a statistically significant predictor of energy equity returns in this model.

---

## ⚙️ Methodology

- Data: XLE, WTI, S&P 500 (yfinance), GPR index  
- Frequency: Daily → Monthly aggregation  
- Model: OLS regression with macro controls  

```python
X = sm.add_constant(df[["gpr", "wti_return", "sp500_return"]])
y = df["return"]

model = sm.OLS(y, X).fit()
```

---

## 🎯 Why This Matters

- Demonstrates how macro risk transmits through commodity markets  
- Highlights indirect pricing mechanisms in financial markets  
- Applies econometrics to real-world financial data  

---

## 📁 Project Structure

```
energy-markets-geopolitical-risk-study/
├── data/
├── notebooks/
├── outputs/
│   ├── charts/
│   └── tables/
├── README.md
└── requirements.txt
```

---

## ▶️ Setup

```bash
pip install -r requirements.txt
```

```bash
jupyter notebook notebooks/analysis.ipynb
```

---

## 👤 Author

Jason Keen

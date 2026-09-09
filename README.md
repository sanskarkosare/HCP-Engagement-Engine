# Omnichannel HCP Engagement Engine
### GLP-1 Drug Targeting | Pharma Commercial Analytics

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

---

## Problem
Pharma sales reps cannot visit every doctor. This engine predicts which Healthcare Providers
are most likely to prescribe GLP-1 drugs and recommends the best outreach channel per HCP.

---

## Results
| Metric | Value |
|---|---|
| AUC-ROC | 0.9732 (vs 0.8616 specialty-only baseline) |
| Cross-validated AUC: 0.9758 ± 0.0004 (5-fold, stratified) |
| Lift over specialty targeting | 112% |
| Model converters/week | 2,981 (vs 1,405 baseline) |
| Cost per conversion | $153 (vs $326 baseline) |
| Savings per conversion | $172 |
| HCPs optimized weekly | 2,867 across 51 territories |

---

## Pipeline

```
CMS Medicare Part D 2024 (15.4M rows, 625K doctors)
        ↓
Feature Engineering (non-GLP-1 volume, prescribing breadth)
        ↓
KMeans Segmentation (k=5) → Champions / GLP1_Rising / Digital_First / Low_Priority / Institutional
        ↓
XGBoost Propensity Model + SHAP Explainability
        ↓
PageRank KOL Detection (KNN similarity graph, same-specialty edges)
        ↓
Thompson Sampling Next-Best-Action (email / rep_visit / webinar)
        ↓
Linear Programming Territory Optimization (budget + visit cap + KOL constraints)
        ↓
Streamlit Dashboard
```

---

## Data
| Source | Type |
|---|---|
| CMS Medicare Part D 2024 | **Real** — 625,608 US prescribers |
| CRM Engagement Layer | **Simulated** — synthetic stand-in for Veeva/Salesforce |

---

## Run Locally

```bash
conda create -n zs_project python=3.10 -y
conda activate zs_project
pip install -r requirements.txt
streamlit run app.py
```

---

## Tech Stack
XGBoost · Scikit-learn · SHAP · NetworkX · PuLP · Streamlit · Plotly · Pandas

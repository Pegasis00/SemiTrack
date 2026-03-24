---
title: SemiTrack India
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
---

## SemiTrack India — Semiconductor Import Substitution Tracker

India semiconductor import bill analysis using CEPII BACI HS92 data.
Tracks HS 8542 (Integrated Circuits) and HS 3818 (Silicon Wafers), 1995–2024.

---

## Project structure

``
SemiTrack/
├── app.py                 ← Gradio dashboard (local + HuggingFace entry point)
├── config.py              ← All paths and constants
├── requirements.txt
├── run_pipeline.py        ← Print the notebook order for the analytics workflow
├── README.md
│
├── notebooks/
│   ├── 01_preprocessing_walkthrough.ipynb
│   ├── 02_eda_walkthrough.ipynb
│   ├── 03_stationarity_walkthrough.ipynb
│   ├── 04_arima_walkthrough.ipynb
│   ├── 05_arimax_walkthrough.ipynb
│   ├── 06_mixshift_walkthrough.ipynb
│   └── 07_policy_report_charts_walkthrough.ipynb
│
├── data/
│   ├── raw/
│   │   └── india_imports_8542_3818_filtered.csv
│   ├── processed/
│   │   ├── india_semiconductor_integrated_annual.csv
│   │   └── india_semiconductor_country_year_breakdown.csv
│   └── synthetic/
│       └── actual_imports_2025_2026.csv   ← demo Micron effect data
│
└── outputs/
    ├── charts/            ← all .png plots
    ├── models/
    └── reports/           ← forecast CSVs, evaluation txt, summaries
``

---

## Setup

```bash
pip install -r requirements.txt
```

---

## Running the pipeline

### Option A — Show the notebook order

```bash
python run_pipeline.py
```

This prints the recommended notebook sequence:

1. Preprocessing and feature engineering
2. EDA — 6 charts saved to `outputs/charts/eda_*.png`
3. Stationarity tests (ADF, KPSS, Chow)
4. ARIMA grid search and baseline forecast
5. ARIMAX with policy dummies
6. Mix shift analysis and delta chart
7. Minister-facing policy report charts

### Option B — Show one specific notebook

```bash
python run_pipeline.py --step 2    # show the EDA notebook path
python run_pipeline.py --step 4    # show the ARIMA notebook path
```

### Option C — Open notebooks directly

```bash
notebooks/01_preprocessing_walkthrough.ipynb
notebooks/02_eda_walkthrough.ipynb
notebooks/03_stationarity_walkthrough.ipynb
notebooks/04_arima_walkthrough.ipynb
notebooks/05_arimax_walkthrough.ipynb
notebooks/06_mixshift_walkthrough.ipynb
notebooks/07_policy_report_charts_walkthrough.ipynb
```

---

## Viewing plots and evaluations

| What you want to see | File to run | Output location |
|---|---|
| EDA overview charts | `notebooks/02_eda_walkthrough.ipynb` | `outputs/charts/eda_01` through `eda_06` |
| Stationarity test plots | `notebooks/03_stationarity_walkthrough.ipynb` | `outputs/charts/stat_01` through `stat_03` |
| ARIMA forecast + residuals + AIC grid | `notebooks/04_arima_walkthrough.ipynb` | `outputs/charts/arima_01` through `arima_03` |
| ARIMAX forecast + ARIMA comparison + coefficients | `notebooks/05_arimax_walkthrough.ipynb` | `outputs/charts/arimax_01` through `arimax_03` |
| Delta chart + mix shift | `notebooks/06_mixshift_walkthrough.ipynb` | `outputs/charts/mixshift_01` and `mixshift_02` |
| Minister report charts | `notebooks/07_policy_report_charts_walkthrough.ipynb` | `outputs/charts/minister_chart_1` through `minister_chart_5` |
| All evaluation metrics | `notebooks/04_arima_walkthrough.ipynb` | `outputs/reports/model_evaluation.csv` |
| ARIMAX text report | `notebooks/05_arimax_walkthrough.ipynb` | `outputs/reports/arimax_evaluation.txt` |
| Stationarity report | `notebooks/03_stationarity_walkthrough.ipynb` | `outputs/reports/stationarity_report.txt` |

**To open plots on Windows:**

```bash
start outputs/charts/eda_01_trajectory.png
start outputs/charts/arimax_01_forecast.png
```

---

## Launching the dashboard

```bash
python app.py
```

Opens at <http://127.0.0.1:7863>

**Substitution Tracker tab:**
Upload `data/synthetic/actual_imports_2025_2026.csv` to see the Micron mix shift effect simulated.
When real 2025–2026 data is available, upload that instead.

---

## Deploying to Hugging Face Spaces

1. Create a new Space at huggingface.co → SDK: Gradio → CPU Basic (free)
2. Clone the empty space:

   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
   ```

3. Copy all files from this folder into the cloned folder
4. Commit and push:

   ```bash
   git add .
   git commit -m "Initial deploy"
   git push
   ```

5. Space goes live in ~2 minutes at `huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`

The `README.md` already has the correct YAML header (`sdk: gradio`, `app_file: app.py`).

---

## Using your real BACI data

If you have the original BACI XLS file:

- Copy it to `data/raw/india_imports_8542_3818_filtered.csv`
- The processed CSVs in `data/processed/` are already your real data
- Replace the synthetic forecast in `outputs/reports/` by working through the modeling notebooks

---

## Pipeline explanation

### Why log-differencing?

The raw import series is non-stationary (ADF p≈0.99). ARIMA requires stationarity.
Log-differencing achieves stationarity (ADF p<0.05) and models proportional growth,
which is appropriate for an exponentially growing series.

### Why ARIMAX over plain ARIMA?

Policy events (2018 inflection, COVID, PLI scheme, Micron MoU) are discrete shocks
not captured by the autocorrelation structure alone. ARIMAX includes these as binary
dummy regressors. If ΔAIC > 2 in favour of ARIMAX, it is the preferred model.

### The mix shift proof

The Micron ATMP plant packages raw semiconductor die (HS 3818 inputs) into finished chips
domestically. This should cause:

- HS 8542 actual imports to fall **below** the BAU forecast (fewer finished chips imported)
- HS 3818 actual imports to spike **above** the BAU forecast (more raw inputs consumed)

Both signals simultaneously cannot be explained by an economic slowdown (which would
reduce both). The divergence is evidence of domestic packaging substituting imports.

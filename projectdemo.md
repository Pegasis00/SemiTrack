# 1. Project Overview

- **Project title:** SemiTrack India - Semiconductor Import Substitution Tracker
- **Objective:** Quantify India's semiconductor import dependence, model business-as-usual (BAU) import trajectories, and detect whether domestic packaging activity is beginning to substitute imported finished chips.
- **Deeper Dive:** For a full file-by-file walkthrough and explanation of the data logic, see [PROJECT_EXPLANATION.md](./PROJECT_EXPLANATION.md).
- **Problem statement:** India imports most semiconductor value chains through two tracked HS groups: `8542` (electronic integrated circuits) and `3818` (doped silicon wafers / electronic chemical elements). Policymakers and industry analysts need a way to distinguish ordinary import growth from genuine domestic substitution effects driven by initiatives such as the PLI scheme and Micron's ATMP investment.
- **Real-world relevance:** The project combines trade analytics, time-series forecasting, and supply-chain risk assessment to answer a practical policy question: is India still only consuming imported chips, or is it beginning to internalize part of the value chain?

SemiTrack is best understood as a research-oriented analytics product rather than a generic dashboard. Its core value is not only visualization, but causal interpretation: it tries to prove import substitution by comparing forecasted BAU imports against observed future imports and checking for a specific two-part "mix shift" signature.

## 2. System Architecture

## High-level architecture

```text
Raw BACI trade CSV
    ->
Processed annual and country-level CSVs
    ->
Python analytics pipeline (steps 1-6)
    ->
Charts + reports + forecast CSVs
    ->
Interactive Gradio dashboard (HTML/JS/Plotly frontend)
    ->
Optional upload of future actual CSVs for substitution detection
```

## Major layers and interactions

| Layer | Main files | Role |
| --- | --- | --- |
| Configuration | `config.py` | Centralizes paths, forecast years, break year, train/validation split, and output directories. |
| Data assets | `data/raw/*.csv`, `data/processed/*.csv`, `data/synthetic/*.csv` | Provide raw trade records, pre-aggregated annual/country datasets, and synthetic future actuals for demo use. |
| Analytics pipeline | `notebooks/01_preprocessing_walkthrough.ipynb` to `notebooks/07_policy_report_charts_walkthrough.ipynb`, `run_pipeline.py` | Walks through data validation, EDA, stationarity and structural-break tests, ARIMA/ARIMAX forecasting, substitution analysis, and minister-facing chart generation. |
| Presentation layer | `app.py` | Serves a custom HTML/CSS/JavaScript dashboard inside Gradio and exposes a lightweight JSON data API for the frontend. |
| Prototype UIs | `Dashboard.html`, `SemiTrack_Dashboard.jsx` | Alternative static and React-based dashboard concepts using hardcoded data. They are design artifacts, not the live runtime path. |
| Outputs | `outputs/charts/`, `outputs/reports/` | Persist generated evidence: 16 chart files, evaluation reports, and forecast CSVs consumed by the dashboard. |

## Technologies used

- **Languages:** Python, HTML, CSS, JavaScript, JSX
- **Core Python libraries:** `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `gradio`
- **Frontend plotting:** Plotly in the live app, Chart.js in `Dashboard.html`, Recharts in `SemiTrack_Dashboard.jsx`
- **Project style:** notebook-driven analytics workflow with file-based artifacts rather than a database-backed application

## 3. Data

## Data sources

| File | Rows | Purpose |
| --- | ---: | --- |
| `data/raw/india_imports_8542_3818_filtered.csv` | 6,261 | Transaction-like BACI trade extract filtered to India imports for HS `8542` and `3818`. |
| `data/processed/india_semiconductor_integrated_annual.csv` | 30 | Annual integrated dataset for 1995-2024 with macro-adjusted values, shares, concentration, and event dummies. |
| `data/processed/india_semiconductor_country_year_breakdown.csv` | 2,253 | Country-year supplier breakdown used for market share, top exporters, and risk analysis. |
| `data/processed/india_semiconductor_integrated_annual_enriched.csv` | 30 | Step 1 output adding engineered features such as logs, differences, lags, rolling means, and squared China share. |
| `data/synthetic/actual_imports_2025_2026.csv` | 6 | Synthetic "future actuals" used to simulate the Micron substitution effect in the dashboard and mix-shift analysis. |

## Key variables in the annual dataset

- Import scale: `import_value_usd_billions`, `real_value_2015usd_billions`, `total_import_value_usd`
- Product composition: `hs8542_import_usd`, `hs3818_import_usd`, `hs8542_share_pct`, `hs3818_share_pct`
- Growth and scale controls: `yoy_nominal_growth_pct`, `yoy_real_growth_pct`, `gdp_deflator_2015_100`
- Supply structure: `china_share_pct`, `supplier_hhi`, `top3_supplier_share_pct`, `num_exporting_countries`, `top_exporter_name`
- Policy/event indicators: `dummy_post_2018_inflection`, `dummy_covid_shock_2020`, `dummy_global_chip_shortage_2021`, `dummy_pli_scheme_launch`, `dummy_micron_mou_2023`
- Engineered features: `log_real_import`, `log_diff`, `first_diff_real`, `rolling3_real`, `lag1_real`, `lag2_real`, `china_share_squared`, `hhi_diff`

## Observed data characteristics

- Coverage is annual from **1995 to 2024**.
- Raw trade value is overwhelmingly concentrated in HS `8542`: roughly **$120.36B** cumulative raw trade value versus **$2.86B** for HS `3818`.
- The 2024 annual snapshot shows **$23.05B nominal imports**, **$14.60B real imports (2015 USD)**, **45.83% China share**, **0.2909 HHI**, and **94 exporting countries**.

## Data flow through the system

1. The repo stores a filtered raw BACI extract and already-prepared processed tables.
2. Notebook Step 1 validates the processed tables against expectations and creates an enriched annual dataset.
3. Notebook Steps 2-7 consume the annual and country tables to generate charts, statistical reports, forecasts, and minister-facing visual assets.
4. `app.py` loads the processed datasets plus the best available forecast artifact.
5. The dashboard optionally accepts uploaded future actuals and compares them against BAU forecasts to produce a substitution verdict.

## 4. Core Functionality

## What the system does, step by step

1. **Validates and enriches the annual dataset.**  
   Step 1 checks missingness in core columns, adds statistical features, and writes `india_semiconductor_integrated_annual_enriched.csv`.
2. **Explains the historical trajectory.**  
   Step 2 produces six EDA charts covering import growth, HS composition, China exposure, supplier concentration, supplier evolution, and feature correlations.
3. **Tests whether forecasting assumptions are defensible.**  
   Step 3 confirms that the level series is non-stationary, the log-differenced series is stationary, and that a structural break occurs around 2018.
4. **Builds a baseline forecast.**  
   Step 4 grid-searches ARIMA orders over `p,q in [0,3]` with `d=1`, trains through 2022, validates on 2023-2024, and forecasts 2025-2027.
5. **Improves the forecast with policy context.**  
   Step 5 extends the baseline to ARIMAX by injecting event dummies for the 2018 inflection, COVID, chip shortage, PLI, and Micron MoU.
6. **Detects substitution via a mix-shift test.**  
   Step 6 decomposes the BAU forecast into HS-specific expectations and looks for a dual signal: `8542` should fall below BAU while `3818` should rise above BAU.
7. **Serves an interactive decision-support dashboard.**  
   `app.py` exposes page-specific data payloads to a custom frontend for Overview, Import Analysis, Substitution Tracker, and Supplier Risk pages.

## Why the workflow matters

- A simple rising import bill does not prove domestic capacity.
- A forecast alone does not explain whether policy shocks matter.
- A post-forecast comparison of finished-chip imports and raw-input imports is the project's central inferential move: it tries to separate true packaging-led substitution from general demand slowdowns.

## 5. Codebase Breakdown

## Folder structure

| Path | Responsibility |
| --- | --- |
| `notebooks/` | Walkthrough notebooks covering preprocessing, EDA, diagnostics, forecasting, substitution analysis, and policy-report charts. |
| `data/raw/` | Filtered BACI raw trade file. |
| `data/processed/` | Pre-aggregated annual and country-level analysis tables. |
| `data/synthetic/` | Demo future actuals for substitution simulation. |
| `outputs/charts/` | Generated PNG evidence from EDA, stationarity, ARIMA, ARIMAX, and mix-shift steps. |
| `outputs/reports/` | Text reports and CSV outputs for model evaluation and forecasts. |
| `outputs/models/` | Reserved output folder; currently unused. |
| `dashboard/` | Present but empty in the current snapshot. |
| `.gradio/flagged/` | Runtime artifact from Gradio flagging; not part of the analytical pipeline. |

## Major files

| File | Responsibility |
| --- | --- |
| `config.py` | Defines all file paths, output directories, forecast constants, and color tokens. |
| `run_pipeline.py` | Prints the ordered notebook workflow or a single notebook path via `--step`. |
| `app.py` | Loads datasets, selects a forecast source, computes page-level metrics, and serves the full dashboard HTML plus a hidden JSON API. |
| `notebooks/01_preprocessing_walkthrough.ipynb` | Validates processed data and engineers statistical features. |
| `notebooks/02_eda_walkthrough.ipynb` | Produces six publication-style charts summarizing history and structure. |
| `notebooks/03_stationarity_walkthrough.ipynb` | Runs ADF, KPSS, and Chow tests and writes the stationarity report. |
| `notebooks/04_arima_walkthrough.ipynb` | Baseline ARIMA model selection, validation, forecasting, diagnostics, and AIC heatmap. |
| `notebooks/05_arimax_walkthrough.ipynb` | ARIMAX forecast using policy dummies and AIC comparison against ARIMA. |
| `notebooks/06_mixshift_walkthrough.ipynb` | BAU-vs-actual substitution logic and two flagship mix-shift charts. |
| `notebooks/07_policy_report_charts_walkthrough.ipynb` | Generates the five minister-facing report charts. |
| `Dashboard.html` | Standalone static dashboard with hardcoded data and client-side CSV parsing. |
| `SemiTrack_Dashboard.jsx` | React/Recharts concept dashboard with hardcoded values and narrative framing. |

## 6. APIs

## API style

The project does not expose a conventional REST backend. Instead, the live dashboard uses Gradio's internal prediction route and wraps it as a lightweight JSON API.

- **Frontend call path:** `POST /run/predict`
- **Backend function:** `api_call(payload_json)` in `app.py`
- **Core dispatcher:** `get_data(page, ...)`

The browser sends a Gradio-formatted body containing a JSON string payload. The backend returns a JSON string describing metrics and chart series for the requested page.

## Supported page payloads

| Page | Input fields | Purpose | Main response contents |
| --- | --- | --- | --- |
| `overview` | `yr` | Top-level import, forecast, concentration, and supplier summary for a selected year. | KPI metrics, HS series, forecast series, China share, HHI, YoY growth, top-5 suppliers. |
| `import` | `yr`, `cyr`, `vm` | Compare one year to another and visualize the 2018 regime shift. | KPI metrics, HS stacks, actual series, pre/post trendlines, comparison table fields. |
| `subst` | `csv_text` | Evaluate uploaded future actuals against BAU forecast. | BAU metrics, historical series, BAU split series, actual `8542` and `3818`, substitution verdict. |
| `risk` | `yr`, `china_r`, `taiwan_r` | Recalculate supply risk using user-adjusted geopolitical risk assumptions. | Composite risk metrics, risk-by-year series, HHI series, supplier matrix/table. |

## Example logical request

```json
{"page":"overview","yr":2024}
```

## Example logical response shape

```json
{
  "metrics": {"bill": {"v":"$23.0B","d":"+14.6% vs 2023","up":true}},
  "chart_years": [1995, 1996, "..."],
  "fc_years": [2025, 2026, 2027]
}
```

## 7. Models / Logic

## Statistical and business logic used

| Logic block | Why it is used | How it works in this project |
| --- | --- | --- |
| Log transform + differencing | Annual semiconductor imports grow non-linearly and violate stationarity assumptions in levels. | The project models `log(real imports)` with `d=1` after testing stationarity, effectively forecasting proportional changes rather than raw levels. |
| ADF and KPSS tests | To justify differencing and avoid mis-specified ARIMA models. | Level series is non-stationary (`ADF p=0.9988`, `KPSS p=0.0195`), while log-differenced series is stationary (`ADF p=0.0`, `KPSS p=0.1`). |
| Chow test | To test whether 2018 marks a structural break. | A break at 2018 is strongly confirmed (`F=242.692`, `p~0`), so the model treats post-2018 behavior as a distinct regime. |
| ARIMA | Baseline univariate forecast of real import growth. | Step 4 searches ARIMA(p,1,q) across small orders and selects `ARIMA(1,1,0)` as best by AIC. |
| ARIMAX | Incorporates discrete policy and shock events that autocorrelation alone cannot explain. | Uses dummies for 2018 inflection, COVID-19, chip shortage, PLI scheme launch, and Micron MoU 2023. The saved report shows an AIC improvement of **5.25** versus the baseline. |
| Supplier HHI | Measures supplier concentration risk. | Computed annually and visualized as a concentration proxy where higher values imply less diversification. |
| Composite geo-risk score | Converts supplier shares into a strategy-oriented risk metric. | Maps exporters to manual geopolitical risk scores and computes a weighted sum using each country's market share. |
| Mix-shift rule | Encodes the core substitution hypothesis. | Domestic packaging should reduce imported finished chips (`8542`) while increasing imported raw inputs (`3818`). Both signals must appear together to count as substitution. |

## Model outputs currently produced

- **Baseline ARIMA order:** `ARIMA(1,1,0)`
- **ARIMA forecast CSV:** `outputs/reports/arima_forecast_values.csv`
- **ARIMAX forecast CSV:** `outputs/reports/arimax_forecast_values.csv`
- **ARIMA evaluation:** `outputs/reports/model_evaluation.csv`
- **ARIMAX evaluation report:** `outputs/reports/arimax_evaluation.txt`

## 8. Workflow / Execution Flow

## Offline analytics flow

1. `run_pipeline.py` launches the six scripts in order.
2. Step 1 loads processed annual and country files plus the filtered raw BACI file.
3. Step 2 visualizes long-run import structure and supplier composition.
4. Step 3 validates the modeling assumptions statistically.
5. Step 4 trains and validates the baseline forecast.
6. Step 5 adds exogenous policy information and produces the preferred BAU forecast.
7. Step 6 translates the total BAU forecast into HS-level expectations and compares them with actual future observations.
8. The pipeline writes artifacts to `outputs/charts/` and `outputs/reports/`.

## Interactive dashboard flow

1. `app.py` loads annual, country, and forecast files at startup.
2. If no forecast artifact is present, the app falls back to a bounded CAGR-based projection.
3. The custom frontend requests page-specific JSON from the hidden Gradio API.
4. Plotly renders the returned arrays into interactive charts.
5. On the Substitution Tracker page, a user uploads a CSV of future actuals.
6. The app parses the CSV in-memory, extracts `2025` values for HS `8542` and `3818`, and recomputes the verdict without retraining the model.

## 9. Key Insights / Behavior

- Imports expanded dramatically from **$0.237B nominal in 1995** to **$23.05B nominal in 2024**.
- In real terms, the series rose from **$0.87B** to **$14.60B**, showing structural acceleration rather than only inflation.
- The post-2018 regime is materially different: mean real growth increased from **10.0%** before 2018 to **34.88%** afterward.
- Supplier concentration worsened after 2018: mean HHI rose from **0.068** to **0.234**.
- China dependence also rose sharply: average China share increased from **13.5%** pre-2018 to **38.5%** post-2018.
- In 2024 the top three suppliers controlled **86.56%** of imports, with **China (45.8%)**, **Taiwan (25.7%)**, and **South Korea (15.0%)** dominating the supply base.
- The current preferred BAU forecast is ARIMAX-based, with a **2025 forecast of $13.93B real imports** and a wide confidence interval of roughly **$9.89B to $19.62B**.
- The synthetic demo file encodes the intended proof case: HS `8542` falls below forecast while HS `3818` rises above forecast, which the project interprets as evidence of domestic packaging activity rather than a simple demand slump.

## 10. Setup & Usage

## Installation

```bash
pip install -r requirements.txt
```

## Main dependencies

- `gradio`
- `pandas`
- `numpy`
- `plotly`
- `scipy`
- `matplotlib`
- `statsmodels`
- `openpyxl`

## Run the full pipeline

```bash
python run_pipeline.py
```

## Run a specific step

```bash
python run_pipeline.py --step 4
```

## Launch the dashboard

```bash
python app.py
```

## Practical notes

- The dashboard launches on **port `7863`** by default.
- The dashboard expects forecast artifacts to exist in `outputs/reports/`; otherwise it falls back to a CAGR estimate.
- To test the substitution logic, upload `data/synthetic/actual_imports_2025_2026.csv` in the Substitution Tracker page.

## 11. Limitations

- **Reproducibility gap:** the repository contains processed annual and country tables, but no script reconstructs them from the raw BACI transaction file. Step 1 validates and enriches data rather than performing the full ETL.
- **Small sample size:** the forecasting model uses only 30 annual observations, with validation effectively limited to 2023-2024.
- **Simplified HS decomposition:** the mix-shift module does not forecast HS `8542` and `3818` separately; it allocates the total BAU forecast using the last historical HS split.
- **Prototype inconsistency:** `Dashboard.html` and `SemiTrack_Dashboard.jsx` contain hardcoded values that are not fully synchronized with the live pipeline outputs and current country shares.
- **Demo-data inconsistency:** the synthetic CSV contains its own BAU values, while `notebooks/06_mixshift_walkthrough.ipynb` derives BAU HS splits from the 2024 composition. These are illustrative, but not fully harmonized.
- **ARIMAX chart bug:** the code attempts to plot coefficient significance in Step 5, but the current output folder lacks `arimax_03_coefficients.png`, consistent with a code path that references `model_full` before it is defined.
- **Monolithic app design:** `app.py` combines backend logic, API dispatch, HTML, CSS, and JavaScript in one file, which limits maintainability.
- **No persisted models:** `outputs/models/` is empty; only reports and forecast CSVs are stored.
- **No automated tests or pinned versions:** dependency versions are unpinned, and there is no unit, integration, or regression test suite.
- **Heuristic risk scoring:** geopolitical risk values are manually assigned, which is useful for exploration but not rigorously calibrated.

## 12. Future Improvements

- Build a reproducible raw-to-processed ETL pipeline so the annual and country tables are generated directly from the BACI extract.
- Forecast HS `8542` and `3818` as separate time series instead of allocating total imports by the latest ratio.
- Add more exogenous drivers such as exchange rates, electronics demand proxies, fab announcements, DGFT monthly releases, and global semiconductor cycle indicators.
- Persist trained model objects and metadata in `outputs/models/` for traceability and reuse.
- Separate the dashboard into a clearer frontend/backend architecture, or at minimum move embedded JavaScript and CSS out of `app.py`.
- Add automated tests for data schema validation, forecast generation, API responses, and substitution verdict logic.
- Version-lock dependencies and document the expected Python version to reduce environment drift.
- Add true backtesting across rolling windows instead of a single short validation split.
- Calibrate supplier risk with external geopolitical or logistics datasets rather than fixed manual scores.
- Reconcile the prototype dashboards, synthetic demo file, README instructions, and live outputs so all presentation layers tell the same numeric story.

## 13. Appendix

## Important configuration constants

| Constant | Value | Meaning |
| --- | --- | --- |
| `BREAK_YEAR` | `2018` | Structural break year used in diagnostics and ARIMAX logic. |
| `TRAIN_END_YEAR` | `2022` | End of model training period. |
| `VAL_START_YEAR` | `2023` | Start of holdout validation period. |
| `FORECAST_YEARS` | `[2025, 2026, 2027]` | Horizon used in ARIMA and ARIMAX forecasts. |

## Primary generated outputs

| Output type | Examples |
| --- | --- |
| EDA charts | `eda_01_trajectory.png` to `eda_06_correlation.png` |
| Diagnostic charts | `stat_01_level_vs_diff.png`, `stat_02_structural_break.png`, `stat_03_acf_pacf.png` |
| Forecast charts | `arima_01_forecast.png`, `arimax_01_forecast.png`, `arimax_02_vs_arima.png` |
| Substitution charts | `mixshift_01_delta.png`, `mixshift_02_hs_split.png` |
| Text/CSV reports | `preprocessing_report.txt`, `stationarity_report.txt`, `arima_summary.txt`, `arimax_evaluation.txt`, `model_evaluation.csv` |

## Bottom-line interpretation

SemiTrack's central contribution is methodological: it turns a policy narrative about semiconductor self-reliance into a measurable signal. The project shows that India's import trajectory accelerated sharply after 2018, that supplier dependence remains highly concentrated, and that ARIMAX is a more credible BAU model than plain ARIMA for this domain. Its substitution proof, however, is still a research prototype: the logic is compelling, but the data engineering, validation depth, and consistency across artifacts need another round of hardening before the system should be treated as production-grade policy infrastructure.

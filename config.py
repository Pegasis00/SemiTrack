"""
config.py — SemiTrack India central configuration
All paths, constants, and palette defined here.
"""
import os

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
OUT_DIR    = os.path.join(BASE_DIR, "outputs")
CHART_DIR  = os.path.join(OUT_DIR, "charts")
MODEL_DIR  = os.path.join(OUT_DIR, "models")
REPORT_DIR = os.path.join(OUT_DIR, "reports")

RAW_FILE     = os.path.join(DATA_DIR, "raw",       "india_imports_8542_3818_filtered.csv")
ANNUAL_FILE  = os.path.join(DATA_DIR, "processed", "india_semiconductor_integrated_annual.csv")
COUNTRY_FILE = os.path.join(DATA_DIR, "processed", "india_semiconductor_country_year_breakdown.csv")
SYNTHETIC_FILE = os.path.join(DATA_DIR, "synthetic", "actual_imports_2025_2026.csv")

FORECAST_FILE_ARIMAX = os.path.join(REPORT_DIR, "arimax_forecast_values.csv")
FORECAST_FILE_ARIMA  = os.path.join(REPORT_DIR, "arima_forecast_values.csv")
MODEL_SUMMARY_FILE   = os.path.join(REPORT_DIR, "model_summary.txt")
EVAL_FILE            = os.path.join(REPORT_DIR, "model_evaluation.csv")

BREAK_YEAR     = 2018
TRAIN_END_YEAR = 2022
VAL_START_YEAR = 2023
FORECAST_YEARS = [2025, 2026, 2027]

COLORS = {
    "hs8542"   : "#1d4ed8",
    "hs3818"   : "#0d9488",
    "forecast" : "#f59e0b",
    "china"    : "#dc2626",
    "green"    : "#16a34a",
    "navy"     : "#0f2744",
    "gray"     : "#64748b",
    "red"      : "#dc2626",
    "amber"    : "#f59e0b",
}

for d in [CHART_DIR, MODEL_DIR, REPORT_DIR,
          os.path.join(DATA_DIR, "synthetic")]:
    os.makedirs(d, exist_ok=True)
